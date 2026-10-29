#!/usr/bin/env python3
"""pg_index_analyzer — анализатор индексов PostgreSQL."""
import argparse
import configparser
import json
import os
import sys
from datetime import datetime
from decimal import Decimal

import psycopg2
import psycopg2.extras


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "db.ini")
DATA_FILE = os.path.join(BASE_DIR, "report_data.js")
REPORT_PAGE = os.path.join(BASE_DIR, "report.html")

DB_DEFAULTS = {
    "host": "localhost",
    "port": "5432",
    "dbname": "index_demo",
    "user": "postgres",
    "password": "",
}


BLOAT_MIN_DEAD_TUPLES = 100
BLOAT_WARN_PCT = 5
BLOAT_CRIT_PCT = 20

CACHE_MIN_ACCESS = 10
CACHE_WARN_PCT = 95
CACHE_CRIT_PCT = 80

MISSING_MIN_SEQ_SCAN = 5
MISSING_MIN_TABLE_BYTES = 512 * 1024
MISSING_CRIT_SEQ_SCAN = 500

USAGE_RARE = 50
USAGE_MODERATE = 500


OK, WARN, DANGER = "ok", "warn", "danger"

RESET = "\033[0m"; BOLD = "\033[1m"
RED = "\033[91m"; YELLOW = "\033[93m"
GREEN = "\033[92m"; CYAN = "\033[96m"; GRAY = "\033[90m"

TERM_COLOR = {OK: GREEN, WARN: YELLOW, DANGER: RED}


SQL_DB_INFO = """
SELECT current_database() AS dbname,
       pg_size_pretty(pg_database_size(current_database())) AS db_size,
       (SELECT count(*) FROM pg_stat_user_tables)  AS table_count,
       (SELECT count(*) FROM pg_stat_user_indexes) AS index_count,
       (SELECT stats_reset FROM pg_stat_database
         WHERE datname = current_database())        AS stats_reset;
"""

SQL_UNUSED = """
SELECT s.schemaname,
       s.relname      AS tablename,
       s.indexrelname AS indexname,
       s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS index_size,
       pg_relation_size(s.indexrelid)                 AS index_size_bytes
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0
  AND NOT i.indisunique
  AND NOT i.indisprimary
  AND NOT EXISTS (SELECT 1 FROM pg_constraint k WHERE k.conindid = s.indexrelid)
ORDER BY pg_relation_size(s.indexrelid) DESC;
"""

SQL_REDUNDANT = """
WITH idx AS (
    SELECT i.indexrelid, i.indrelid, i.indisunique, i.indnatts, i.indnkeyatts,
           n.nspname AS schemaname, t.relname AS tablename, c.relname AS indexname,
           c.relam,
           string_to_array(i.indkey::text, ' ')                          AS allkeys,
           (string_to_array(i.indkey::text, ' '))[1:i.indnkeyatts]       AS keys,
           (string_to_array(i.indclass::text, ' '))[1:i.indnkeyatts]     AS classes,
           (string_to_array(i.indcollation::text, ' '))[1:i.indnkeyatts] AS colls,
           (string_to_array(i.indoption::text, ' '))[1:i.indnkeyatts]    AS opts,
           coalesce(pg_get_expr(i.indexprs, i.indrelid), '')             AS exprs,
           coalesce(pg_get_expr(i.indpred,  i.indrelid), '')             AS pred,
           (i.indisprimary OR EXISTS (
                SELECT 1 FROM pg_constraint k WHERE k.conindid = i.indexrelid)) AS has_constraint,
           coalesce(st.idx_scan, 0) AS scans
    FROM pg_index i
    LEFT JOIN pg_stat_user_indexes st ON st.indexrelid = i.indexrelid
    JOIN pg_class c     ON c.oid = i.indexrelid
    JOIN pg_class t     ON t.oid = i.indrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE i.indisvalid
      AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
)
SELECT DISTINCT ON (a.indexrelid)
       a.schemaname,
       a.tablename,
       a.indexname,
       b.indexname AS kept_index,
       CASE WHEN a.allkeys = b.allkeys THEN 'дубль' ELSE 'префикс' END AS kind,
       pg_size_pretty(pg_relation_size(a.indexrelid)) AS index_size,
       pg_relation_size(a.indexrelid)                 AS index_size_bytes
FROM idx a
JOIN idx b ON a.indrelid = b.indrelid
          AND a.indexrelid <> b.indexrelid
          AND a.pred = b.pred
WHERE NOT a.has_constraint
  AND (
        ( a.relam = b.relam
          AND a.allkeys = b.allkeys
          AND a.classes = b.classes
          AND a.colls   = b.colls
          AND a.opts    = b.opts
          AND a.exprs   = b.exprs
          AND (b.indisunique OR NOT a.indisunique)
          AND (b.has_constraint OR b.scans > a.scans
               OR (b.scans = a.scans AND a.indexrelid > b.indexrelid)) )
     OR ( a.relam = 403 AND b.relam = 403
          AND NOT a.indisunique
          AND a.indnatts = a.indnkeyatts
          AND a.exprs = '' AND b.exprs = ''
          AND a.indnkeyatts < b.indnkeyatts
          AND b.keys[1:a.indnkeyatts]    = a.keys
          AND b.classes[1:a.indnkeyatts] = a.classes
          AND b.colls[1:a.indnkeyatts]   = a.colls
          AND b.opts[1:a.indnkeyatts]    = a.opts )
      )
ORDER BY a.indexrelid, (a.allkeys = b.allkeys) DESC, b.indnkeyatts;
"""

SQL_BLOAT = """
SELECT schemaname, relname AS tablename,
       n_dead_tup, n_live_tup,
       CASE WHEN n_live_tup > 0
            THEN round(100.0 * n_dead_tup / n_live_tup, 1)
            ELSE 0 END AS dead_ratio_pct,
       last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > %(min_dead)s
ORDER BY n_dead_tup DESC LIMIT 20;
"""

SQL_MISSING = """
SELECT schemaname, relname AS tablename,
       seq_scan, seq_tup_read,
       COALESCE(idx_scan, 0) AS idx_scan,
       CASE WHEN seq_scan > 0 THEN (seq_tup_read / seq_scan)::BIGINT ELSE 0 END AS avg_rows_per_seqscan,
       pg_size_pretty(pg_relation_size(relid)) AS table_size
FROM pg_stat_user_tables
WHERE seq_scan > %(min_seq)s
  AND COALESCE(idx_scan, 0) < seq_scan
  AND pg_relation_size(relid) > %(min_bytes)s
ORDER BY seq_tup_read DESC LIMIT 10;
"""

SQL_CACHE = """
SELECT s.schemaname, s.indexrelname AS index_name, s.relname AS table_name,
       s.idx_blks_hit, s.idx_blks_read,
       round(100.0 * s.idx_blks_hit / NULLIF(s.idx_blks_hit + s.idx_blks_read, 0), 1) AS cache_hit_pct
FROM pg_statio_user_indexes s
WHERE (s.idx_blks_hit + s.idx_blks_read) >= %(min_access)s
ORDER BY cache_hit_pct ASC LIMIT 15;
"""

SQL_USAGE = """
SELECT s.schemaname, s.relname AS tablename, s.indexrelname AS indexname,
       s.idx_scan, s.idx_tup_read,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS index_size,
       (i.indisprimary OR i.indisunique OR EXISTS (
            SELECT 1 FROM pg_constraint k WHERE k.conindid = s.indexrelid)) AS is_constraint
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
ORDER BY s.idx_scan DESC, s.indexrelname;
"""


def normalize(row):
    out = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            v = float(v)
        elif isinstance(v, datetime):
            v = v.strftime("%Y-%m-%d %H:%M:%S")
        out[k] = v
    return out


def fetch(cur, sql, params=None):
    cur.execute(sql, params)
    return [normalize(r) for r in cur.fetchall()]


def cell(v):
    return "—" if v is None else str(v)


def num(v):
    return 0.0 if v is None else float(v)


def fmt_bytes(b):
    for u in ["Б", "КБ", "МБ", "ГБ"]:
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} ТБ"


def plural(n, one, few, many):
    n = abs(int(n))
    if 11 <= n % 100 <= 14:
        return many
    r = n % 10
    return one if r == 1 else few if 2 <= r <= 4 else many


def count_word(n, one, few, many):
    return f"{n} {plural(n, one, few, many)}"


def bloat_level(r):
    p = num(r.get("dead_ratio_pct"))
    return DANGER if p > BLOAT_CRIT_PCT else WARN if p > BLOAT_WARN_PCT else OK


def cache_level(r):
    p = num(r.get("cache_hit_pct"))
    return DANGER if p < CACHE_CRIT_PCT else WARN if p < CACHE_WARN_PCT else OK


def missing_level(r):
    return DANGER if num(r.get("seq_scan")) > MISSING_CRIT_SEQ_SCAN else WARN


def usage_label(r):
    if r.get("is_constraint"):
        return "ограничение (PK/unique)"
    n = r.get("idx_scan") or 0
    if n == 0:
        return "не используется"
    if n < USAGE_RARE:
        return "редко"
    if n < USAGE_MODERATE:
        return "умеренно"
    return "активно"


def usage_level(r):
    lbl = r.get("usage_label")
    return DANGER if lbl == "не используется" else WARN if lbl == "редко" else OK


SECTION_LEVELS = {
    "unused": lambda r: WARN,
    "redundant": lambda r: DANGER,
    "bloat": bloat_level,
    "missing": missing_level,
    "cache": cache_level,
    "usage": usage_level,
}


def load_db_config(path):
    cfg = dict(DB_DEFAULTS)
    if not os.path.exists(path):
        print(f"{YELLOW}⚠ Файл настроек не найден: {path}\n"
              f"  Скопируйте db.example.ini в db.ini и впишите свой пароль.{RESET}")
        return cfg
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(path, encoding="utf-8")
    if not parser.has_section("database"):
        print(f"{YELLOW}⚠ В {path} нет секции [database], используются значения по умолчанию{RESET}")
        return cfg
    for key in DB_DEFAULTS:
        if parser.has_option("database", key):
            cfg[key] = parser.get("database", key).strip()
    return cfg


def collect(cur):
    data = {"db_info": fetch(cur, SQL_DB_INFO)[0]}
    data["unused"] = fetch(cur, SQL_UNUSED)
    data["redundant"] = fetch(cur, SQL_REDUNDANT)
    data["bloat"] = fetch(cur, SQL_BLOAT, {"min_dead": BLOAT_MIN_DEAD_TUPLES})
    data["missing"] = fetch(cur, SQL_MISSING,
                            {"min_seq": MISSING_MIN_SEQ_SCAN, "min_bytes": MISSING_MIN_TABLE_BYTES})
    data["cache"] = fetch(cur, SQL_CACHE, {"min_access": CACHE_MIN_ACCESS})
    data["usage"] = fetch(cur, SQL_USAGE)
    for r in data["usage"]:
        r["usage_label"] = usage_label(r)
    return data


def summarize(data):
    drop = {}
    for r in data["unused"] + data["redundant"]:
        drop[(r["schemaname"], r["indexname"])] = r.get("index_size_bytes") or 0
    bloat_bad = [r for r in data["bloat"] if bloat_level(r) != OK]
    return {
        "unused": len(data["unused"]),
        "redundant": len(data["redundant"]),
        "index_problems": len(drop),
        "reclaimable_bytes": sum(drop.values()),
        "bloat_crit": sum(1 for r in bloat_bad if bloat_level(r) == DANGER),
        "bloat_bad": len(bloat_bad),
        "missing": len(data["missing"]),
        "total": len(drop) + len(bloat_bad) + len(data["missing"]),
    }


def stats_note(db_info):
    reset = db_info.get("stats_reset")
    since = f"с {reset}" if reset else "с момента создания БД (сброса не было)"
    return f"Нулевое число сканирований считается {since}. На репликах статистика отдельная."


def export_data(data, s, path):
    payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "db": data["db_info"],
        "stats_note": stats_note(data["db_info"]),
        "summary": dict(s, reclaimable_pretty=fmt_bytes(s["reclaimable_bytes"])),
        "cache_min_access": CACHE_MIN_ACCESS,
        "sections": {
            name: [dict(r, level=level_fn(r)) for r in data[name]]
            for name, level_fn in SECTION_LEVELS.items()
        },
    }
    body = json.dumps(payload, ensure_ascii=False, indent=1, default=str)
    with open(path, "w", encoding="utf-8") as f:
        f.write("// Сгенерировано main.py — не редактируйте вручную.\n")
        f.write(f"window.REPORT_DATA = {body};\n")


def hdr(title):
    print(f"\n{BOLD}{CYAN}{'─' * 60}\n  {title}\n{'─' * 60}{RESET}")


def print_tbl(rows, cols, level_fn=None):
    if not rows:
        print(f"  {GREEN}✓ Нет данных{RESET}")
        return
    w = {c: len(c) for c in cols}
    for r in rows:
        for c in cols:
            w[c] = max(w[c], len(cell(r.get(c))))
    print("  " + "  ".join(f"{BOLD}{c:<{w[c]}}{RESET}" for c in cols))
    print("  " + "  ".join("─" * w[c] for c in cols))
    for r in rows:
        clr = TERM_COLOR[level_fn(r)] if level_fn else ""
        print(f"  {clr}" + "  ".join(f"{cell(r.get(c)):<{w[c]}}" for c in cols) + RESET)


def print_report(data, s):
    hdr("1. НЕИСПОЛЬЗУЕМЫЕ ИНДЕКСЫ")
    print(f"  {GRAY}{stats_note(data['db_info'])}{RESET}")
    if data["unused"]:
        print(f"  {YELLOW}⚠ Найдено: {len(data['unused'])}{RESET}\n")
        print_tbl(data["unused"], ["tablename", "indexname", "index_size", "idx_scan"],
                  SECTION_LEVELS["unused"])
        total = sum(r["index_size_bytes"] or 0 for r in data["unused"])
        print(f"\n  {RED}Итого занято впустую: {fmt_bytes(total)}{RESET}")
    else:
        print(f"  {GREEN}✓ Все индексы используются{RESET}")

    hdr("2. ЛИШНИЕ ИНДЕКСЫ (дубли и префиксы)")
    if data["redundant"]:
        print(f"  {RED}✗ Найдено: {len(data['redundant'])}{RESET}\n")
        print_tbl(data["redundant"], ["tablename", "indexname", "kept_index", "kind", "index_size"],
                  SECTION_LEVELS["redundant"])
    else:
        print(f"  {GREEN}✓ Лишних индексов нет{RESET}")

    hdr("3. РАЗДУВАНИЕ ТАБЛИЦ (мёртвые кортежи)")
    if data["bloat"]:
        print_tbl(data["bloat"],
                  ["tablename", "n_live_tup", "n_dead_tup", "dead_ratio_pct", "last_autovacuum"],
                  bloat_level)
    else:
        print(f"  {GREEN}✓ Мёртвых кортежей практически нет{RESET}")

    hdr("4. ВЕРОЯТНО ОТСУТСТВУЮЩИЕ ИНДЕКСЫ")
    if data["missing"]:
        print(f"  {YELLOW}⚠ Таблицы с частым Seq Scan:{RESET}\n")
        print_tbl(data["missing"],
                  ["tablename", "seq_scan", "idx_scan", "avg_rows_per_seqscan", "table_size"],
                  missing_level)
    else:
        print(f"  {GREEN}✓ Подозрительных Seq Scan нет{RESET}")

    hdr("5. КЭШ ИНДЕКСОВ")
    if data["cache"]:
        print_tbl(data["cache"],
                  ["index_name", "table_name", "idx_blks_hit", "idx_blks_read", "cache_hit_pct"],
                  cache_level)
    else:
        print(f"  {GRAY}Недостаточно обращений для оценки (порог: {CACHE_MIN_ACCESS}){RESET}")

    hdr("6. СТАТИСТИКА ИСПОЛЬЗОВАНИЯ")
    print_tbl(data["usage"],
              ["tablename", "indexname", "idx_scan", "index_size", "usage_label"], usage_level)

    hdr("ИТОГ")
    lines = []
    if s["unused"]:
        lines.append(f"{RED}✗ {count_word(s['unused'], 'неиспользуемый индекс', 'неиспользуемых индекса', 'неиспользуемых индексов')}{RESET}")
    if s["redundant"]:
        lines.append(f"{RED}✗ {count_word(s['redundant'], 'лишний индекс', 'лишних индекса', 'лишних индексов')}{RESET}")
    if s["bloat_bad"]:
        lines.append(f"{YELLOW}⚠ {count_word(s['bloat_bad'], 'таблица', 'таблицы', 'таблиц')} с мёртвыми кортежами "
                     f"(критичных: {s['bloat_crit']}){RESET}")
    if s["missing"]:
        lines.append(f"{YELLOW}⚠ {count_word(s['missing'], 'таблица', 'таблицы', 'таблиц')} с подозрительным Seq Scan{RESET}")
    if lines:
        for ln in lines:
            print(f"  {ln}")
        print(f"\n  Всего проблем: {BOLD}{s['total']}{RESET}"
              f" (индекс, попавший в обе категории, считается один раз)")
        if s["reclaimable_bytes"]:
            print(f"  Можно освободить: {BOLD}{fmt_bytes(s['reclaimable_bytes'])}{RESET}")
    else:
        print(f"  {GREEN}{BOLD}✓ Индексы в хорошем состоянии{RESET}")
    print(f"\n  {GRAY}Сформировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")


def setup_console():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if os.name == "nt":
        os.system("")


def parse_args():
    ap = argparse.ArgumentParser(
        description="Анализатор индексов PostgreSQL. Подключение берётся из db.ini, "
                    "аргументы ниже его переопределяют.")
    ap.add_argument("--config", default=CONFIG_FILE, help="файл настроек (по умолчанию db.ini рядом с main.py)")
    ap.add_argument("--host")
    ap.add_argument("--port", type=int)
    ap.add_argument("--dbname")
    ap.add_argument("--user")
    ap.add_argument("--no-report", action="store_true", help="не сохранять данные для report.html")
    return ap.parse_args()


def main():
    setup_console()
    args = parse_args()

    cfg = load_db_config(args.config)
    for key in ("host", "port", "dbname", "user"):
        if getattr(args, key) is not None:
            cfg[key] = str(getattr(args, key))

    print(f"\n{BOLD}pg_index_analyzer — {cfg['dbname']}{RESET}")

    try:
        conn = psycopg2.connect(host=cfg["host"], port=int(cfg["port"]), dbname=cfg["dbname"],
                                user=cfg["user"],
                                password=cfg["password"] or None)
        conn.set_session(readonly=True, autocommit=True)
        print(f"{GREEN}✓ Подключено (read-only){RESET}")
    except psycopg2.Error as e:
        print(f"{RED}✗ Ошибка подключения: {str(e).strip()}{RESET}")
        if not cfg["password"]:
            print(f"{YELLOW}  Пароль не задан: впишите его в {args.config} (строка password = ...){RESET}")
        return 1

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            data = collect(cur)
    except psycopg2.Error as e:
        print(f"{RED}✗ Ошибка запроса: {str(e).strip()}{RESET}")
        return 1
    finally:
        conn.close()

    summary = summarize(data)
    print_report(data, summary)

    if not args.no_report:
        export_data(data, summary, DATA_FILE)
        print(f"  {GREEN}✓ Данные для отчёта сохранены: {DATA_FILE}{RESET}")
        print(f"  {GREEN}  Откройте в браузере: {REPORT_PAGE}{RESET}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

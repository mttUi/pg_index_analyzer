// Сгенерировано main.py — не редактируйте вручную.
window.REPORT_DATA = {
 "generated_at": "2026-10-29 21:07:27",
 "db": {
  "dbname": "index_demo",
  "db_size": "111 MB",
  "table_count": 6,
  "index_count": 18,
  "stats_reset": null
 },
 "stats_note": "Нулевое число сканирований считается с момента создания БД (сброса не было). На репликах статистика отдельная.",
 "summary": {
  "unused": 3,
  "redundant": 2,
  "index_problems": 4,
  "reclaimable_bytes": 10584064,
  "bloat_crit": 1,
  "bloat_bad": 2,
  "missing": 2,
  "total": 8,
  "reclaimable_pretty": "10.1 МБ"
 },
 "cache_min_access": 10,
 "sections": {
  "unused": [
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_user_id",
    "idx_scan": 0,
    "index_size": "3656 kB",
    "index_size_bytes": 3743744,
    "level": "warn"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_region_unused",
    "idx_scan": 0,
    "index_size": "2200 kB",
    "index_size_bytes": 2252800,
    "level": "warn"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_upper_region",
    "idx_scan": 0,
    "index_size": "2200 kB",
    "index_size_bytes": 2252800,
    "level": "warn"
   }
  ],
  "redundant": [
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_user_id",
    "kept_index": "idx_orders_uid_old",
    "kind": "дубль",
    "index_size": "3656 kB",
    "index_size_bytes": 3743744,
    "level": "danger"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_status_duplicate",
    "kept_index": "idx_orders_status_date",
    "kind": "префикс",
    "index_size": "2280 kB",
    "index_size_bytes": 2334720,
    "level": "danger"
   }
  ],
  "bloat": [
   {
    "schemaname": "public",
    "tablename": "orders",
    "n_dead_tup": 115182,
    "n_live_tup": 203000,
    "dead_ratio_pct": 56.7,
    "last_autovacuum": null,
    "last_autoanalyze": null,
    "level": "danger"
   },
   {
    "schemaname": "public",
    "tablename": "events",
    "n_dead_tup": 22670,
    "n_live_tup": 182330,
    "dead_ratio_pct": 12.4,
    "last_autovacuum": "2026-10-29 19:26:25",
    "last_autoanalyze": "2026-10-29 21:07:26",
    "level": "warn"
   }
  ],
  "missing": [
   {
    "schemaname": "public",
    "tablename": "events",
    "seq_scan": 116,
    "seq_tup_read": 11600050,
    "idx_scan": 50,
    "avg_rows_per_seqscan": 100000,
    "table_size": "21 MB",
    "level": "warn"
   },
   {
    "schemaname": "public",
    "tablename": "audit_log",
    "seq_scan": 51,
    "seq_tup_read": 2550000,
    "idx_scan": 0,
    "avg_rows_per_seqscan": 50000,
    "table_size": "2656 kB",
    "level": "warn"
   }
  ],
  "cache": [
   {
    "schemaname": "public",
    "index_name": "idx_users_del",
    "table_name": "users",
    "idx_blks_hit": 41,
    "idx_blks_read": 3,
    "cache_hit_pct": 93.2,
    "level": "warn"
   },
   {
    "schemaname": "public",
    "index_name": "uq_users_email",
    "table_name": "users",
    "idx_blks_hit": 1563,
    "idx_blks_read": 101,
    "cache_hit_pct": 93.9,
    "level": "warn"
   },
   {
    "schemaname": "public",
    "index_name": "idx_order_items_order",
    "table_name": "order_items",
    "idx_blks_hit": 7124,
    "idx_blks_read": 429,
    "cache_hit_pct": 94.3,
    "level": "warn"
   },
   {
    "schemaname": "public",
    "index_name": "idx_order_items_product",
    "table_name": "order_items",
    "idx_blks_hit": 11690,
    "idx_blks_read": 175,
    "cache_hit_pct": 98.5,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "idx_orders_uid_old",
    "table_name": "orders",
    "idx_blks_hit": 328745,
    "idx_blks_read": 228,
    "cache_hit_pct": 99.9,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "idx_orders_status_duplicate",
    "table_name": "orders",
    "idx_blks_hit": 236457,
    "idx_blks_read": 171,
    "cache_hit_pct": 99.9,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "idx_orders_big_partial",
    "table_name": "orders",
    "idx_blks_hit": 48357,
    "idx_blks_read": 37,
    "cache_hit_pct": 99.9,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "idx_orders_status_date",
    "table_name": "orders",
    "idx_blks_hit": 334081,
    "idx_blks_read": 174,
    "cache_hit_pct": 99.9,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "idx_orders_user_id",
    "table_name": "orders",
    "idx_blks_hit": 323409,
    "idx_blks_read": 228,
    "cache_hit_pct": 99.9,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "idx_orders_upper_region",
    "table_name": "orders",
    "idx_blks_hit": 360690,
    "idx_blks_read": 176,
    "cache_hit_pct": 100.0,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "products_pkey",
    "table_name": "products",
    "idx_blks_hit": 12920,
    "idx_blks_read": 1,
    "cache_hit_pct": 100.0,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "orders_pkey",
    "table_name": "orders",
    "idx_blks_hit": 715543,
    "idx_blks_read": 1,
    "cache_hit_pct": 100.0,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "order_items_pkey",
    "table_name": "order_items",
    "idx_blks_hit": 353259,
    "idx_blks_read": 1,
    "cache_hit_pct": 100.0,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "events_pkey",
    "table_name": "events",
    "idx_blks_hit": 355290,
    "idx_blks_read": 1,
    "cache_hit_pct": 100.0,
    "level": "ok"
   },
   {
    "schemaname": "public",
    "index_name": "idx_orders_region_unused",
    "table_name": "orders",
    "idx_blks_hit": 360690,
    "idx_blks_read": 176,
    "cache_hit_pct": 100.0,
    "level": "ok"
   }
  ],
  "usage": [
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "orders_pkey",
    "idx_scan": 4861,
    "idx_tup_read": 18993,
    "index_size": "8928 kB",
    "is_constraint": true,
    "usage_label": "ограничение (PK/unique)",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "products",
    "indexname": "products_pkey",
    "idx_scan": 4658,
    "idx_tup_read": 4658,
    "index_size": "64 kB",
    "is_constraint": true,
    "usage_label": "ограничение (PK/unique)",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "order_items",
    "indexname": "idx_order_items_product",
    "idx_scan": 2930,
    "idx_tup_read": 54281,
    "index_size": "1408 kB",
    "is_constraint": false,
    "usage_label": "активно",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_uid_old",
    "idx_scan": 1912,
    "idx_tup_read": 24137,
    "index_size": "3656 kB",
    "is_constraint": false,
    "usage_label": "активно",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "users",
    "indexname": "users_pkey",
    "idx_scan": 1762,
    "idx_tup_read": 1762,
    "index_size": "456 kB",
    "is_constraint": true,
    "usage_label": "ограничение (PK/unique)",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "order_items",
    "indexname": "idx_order_items_order",
    "idx_scan": 1500,
    "idx_tup_read": 1509,
    "index_size": "3936 kB",
    "is_constraint": false,
    "usage_label": "активно",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "users",
    "indexname": "uq_users_email",
    "idx_scan": 830,
    "idx_tup_read": 830,
    "index_size": "808 kB",
    "is_constraint": true,
    "usage_label": "ограничение (PK/unique)",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_status_date",
    "idx_scan": 696,
    "idx_tup_read": 138906,
    "index_size": "3328 kB",
    "is_constraint": false,
    "usage_label": "активно",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_big_partial",
    "idx_scan": 100,
    "idx_tup_read": 1356600,
    "index_size": "512 kB",
    "is_constraint": false,
    "usage_label": "умеренно",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_lower_region",
    "idx_scan": 60,
    "idx_tup_read": 1603608,
    "index_size": "2200 kB",
    "is_constraint": false,
    "usage_label": "умеренно",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "events",
    "indexname": "idx_events_payload",
    "idx_scan": 50,
    "idx_tup_read": 714,
    "index_size": "4848 kB",
    "is_constraint": false,
    "usage_label": "умеренно",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "users",
    "indexname": "idx_users_del",
    "idx_scan": 20,
    "idx_tup_read": 8000,
    "index_size": "152 kB",
    "is_constraint": false,
    "usage_label": "редко",
    "level": "warn"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_status_duplicate",
    "idx_scan": 1,
    "idx_tup_read": 69369,
    "index_size": "2280 kB",
    "is_constraint": false,
    "usage_label": "редко",
    "level": "warn"
   },
   {
    "schemaname": "public",
    "tablename": "events",
    "indexname": "events_pkey",
    "idx_scan": 0,
    "idx_tup_read": 0,
    "index_size": "4512 kB",
    "is_constraint": true,
    "usage_label": "ограничение (PK/unique)",
    "level": "ok"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_region_unused",
    "idx_scan": 0,
    "idx_tup_read": 0,
    "index_size": "2200 kB",
    "is_constraint": false,
    "usage_label": "не используется",
    "level": "danger"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_upper_region",
    "idx_scan": 0,
    "idx_tup_read": 0,
    "index_size": "2200 kB",
    "is_constraint": false,
    "usage_label": "не используется",
    "level": "danger"
   },
   {
    "schemaname": "public",
    "tablename": "orders",
    "indexname": "idx_orders_user_id",
    "idx_scan": 0,
    "idx_tup_read": 0,
    "index_size": "3656 kB",
    "is_constraint": false,
    "usage_label": "не используется",
    "level": "danger"
   },
   {
    "schemaname": "public",
    "tablename": "order_items",
    "indexname": "order_items_pkey",
    "idx_scan": 0,
    "idx_tup_read": 0,
    "index_size": "4472 kB",
    "is_constraint": true,
    "usage_label": "ограничение (PK/unique)",
    "level": "ok"
   }
  ]
 }
};

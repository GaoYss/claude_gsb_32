#!/usr/bin/env sh
set -e

if [ -n "${DATABASE_URL:-}" ]; then
  echo "等待数据库就绪..."
  python - <<'PY'
import os
import sys
import time

from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL"]
engine = create_engine(url)

for attempt in range(1, 31):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("数据库已就绪")
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001
        print(f"第 {attempt} 次连接失败：{exc}")
        time.sleep(2)

print("数据库连接超时")
sys.exit(1)
PY
fi

echo "初始化数据表..."
python -m flask --app wsgi init-db

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
  echo "写入演示数据..."
  python -m flask --app wsgi seed --reset
fi

exec "$@"

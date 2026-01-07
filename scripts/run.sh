#!/bin/sh

# 에러 발생 시 즉시 중단
set -e

echo "APP_ENV=$APP_ENV"
echo "DEBUG=$DEBUG"

# 정적 파일 수집 (배포 환경에서 중요)
if [ "$DEBUG" = "False" ]; then
    uv run python manage.py collectstatic --noinput
fi

# 모델 변경사항이 있는데 migration 파일이 없는지 확인
uv run python manage.py makemigrations --check --noinput

# DB 테이블 생성/업데이트
uv run python manage.py migrate --noinput

# 웹 서버 실행
if [ "$DEBUG" = "True" ]; then
    echo "개발용 서버를 실행합니다. (runserver)"
    uv run python manage.py runserver 0.0.0.0:8000
else
    echo "배포용 서버를 실행합니다. (gunicorn)"
    uv run gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 2 \
        --log-level info
fi

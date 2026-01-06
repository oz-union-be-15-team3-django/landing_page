#!/bin/sh

# 에러 발생 시 즉시 중단
set -e

# 모델 변경사항이 있는데 migration 파일이 없는지 확인
uv run python manage.py makemigrations --check --noinput

# DB 테이블 생성/업데이트
uv run python manage.py migrate --noinput

# 배포용 웹 서버(Gunicorn) 실행
uv run gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2
# if [ "$DEBUG" = "True" ]; then
#     uv run python manage.py runserver 0.0.0.0:8000
# else
#     uv run gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2
# fi

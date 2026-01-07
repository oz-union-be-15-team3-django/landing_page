# 베이스 이미지 설정
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 작업 디렉토리 설정
WORKDIR /landing_page

# uv 바이너리 복사
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 의존성 파일 복사 및 설치 (캐싱 활용)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

# 프로젝트 전체 파일 복사
COPY . .

# 프로젝트 설치
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 실행 환경 구성 (가상환경 경로 설정)
ENV PATH="/app/.venv/bin:$PATH"

# 포트 개방
EXPOSE 8000

# 스크립트를 사용하여 애플리케이션 실행
RUN chmod +x ./scripts/run.sh

# 컨테이너 실행 시 스크립트 실행
CMD ["/scripts/run.sh"]
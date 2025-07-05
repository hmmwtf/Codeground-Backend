# 1. Python 3.11.9 slim 기반 이미지 사용
FROM python:3.11.9-slim

# 2. 환경변수 설정 (timezone, python 캐싱 off, poetry 가상환경 off)
ARG TZ=Asia/Seoul
ENV TZ=${TZ} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.3 \
    # poetry가 venv를 따로 만들지 않도록 설정
    POETRY_VIRTUALENVS_CREATE=false

# 3. 의존성 및 Poetry 설치 (PostgreSQL 헤더/컴파일러 포함)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc libpq-dev curl && \
    curl -sSL https://install.python-poetry.org | python - && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 4. Poetry 경로를 PATH에 추가
ENV PATH="/root/.local/bin:$PATH"

# 5. 작업 디렉토리 지정 (최상위 루트: alembic.ini, migration 폴더가 여기 위치해야 함)
WORKDIR /

# 6. pyproject.toml, poetry.lock, README.md, alembic.ini 파일 복사 (alembic.ini 꼭 포함)
COPY pyproject.toml poetry.lock README.md alembic.ini ./

# 7. src와 migration 폴더 모두 복사 (alembic migration 폴더 꼭 포함)
COPY src/ ./src
COPY migration/ ./migration

# 8. Poetry로 패키지 설치 (메인 의존성만)
RUN poetry install --only main --no-interaction --no-ansi

# 9. FastAPI가 사용할 포트 오픈
EXPOSE 8000

# 10. 컨테이너 시작 시 Alembic migration → FastAPI 서버 실행 (둘 다 Poetry 환경에서)
CMD ["bash", "-c", "poetry run alembic upgrade head && poetry run uvicorn src.app.main:app --host 0.0.0.0 --port 8000"]
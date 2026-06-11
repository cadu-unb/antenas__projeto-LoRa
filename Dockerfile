FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY src/ ./src/

EXPOSE 3953

CMD ["uv", "run", "streamlit", "run", "src/lora_antenna/app.py", \
     "--server.port", "3953", "--server.address", "0.0.0.0"]

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make swig git autoconf automake libtool pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
# PyPI PyNEC 1.7.3.6 sdist ships broken 15KB pre-built stub — build from GitHub instead
RUN uv sync --frozen --no-dev

# Build PyNEC from GitHub source following build.sh steps
RUN uv pip install numpy setuptools \
    && git clone --depth=1 https://github.com/tmolteno/python-necpp.git /tmp/pynecpp \
    && cd /tmp/pynecpp \
    && git submodule update --init --depth=1 \
    && cd PyNEC \
    && ln -s ../necpp_src . \
    && cd ../necpp_src \
    && make -f Makefile.git \
    && ./configure --without-lapack \
    && cd ../PyNEC \
    && swig -Wall -c++ -python PyNEC.i \
    && /app/.venv/bin/python setup.py install \
    && rm -rf /tmp/pynecpp

COPY backend/ ./backend/
COPY frontend/ ./frontend/

CMD ["uv", "run", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

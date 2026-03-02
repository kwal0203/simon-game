FROM python:3.12-slim
WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# Copy source code
COPY . .
EXPOSE 8080

# Setup a user so we don't use root
RUN useradd -m -d /home/app app && chown -R app:app /app
USER app
ENV HOME=/home/app

CMD ["uv", "run", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8080"]

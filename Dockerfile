# Use python:3.12-slim as the base image
FROM python:3.12-slim

# Install necessary dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    python3-dev \
    liblz4-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Set UV_VENV_PATH to the location of the virtual environment
ENV UV_VENV_PATH="/opt/docker.venv"

# Set a custom virtual environment name
ENV VIRTUAL_ENV="/opt/docker.venv"

# Place executables in the environment at the front of the path
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy all files to the container
COPY . .

# Set UV_PROJECT_PATH to the location of the project
ENV UV_PROJECT_ENVIRONMENT="/opt/docker.venv/"

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --active

# Then, add the rest of the project source code and install it
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --active

# Collecting static files command
RUN uv run python manage.py collectstatic --noinput

# Change permissions of the entrypoint script
RUN chmod +x /app/docker-entrypoint.sh

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]

# Expose the port the app will run on
EXPOSE 8000

# Run the Django server ASGI
CMD ["uv", "run", "uvicorn", "core.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload"]

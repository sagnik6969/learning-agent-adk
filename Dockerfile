FROM ghcr.io/astral-sh/uv:bookworm-slim
WORKDIR /app
COPY pyproject.toml .
COPY .python-version .
RUN uv sync
COPY . .
RUN ls
EXPOSE 3535
CMD [ "uv","run","adk","web","--port","3535","--host","0.0.0.0" ]
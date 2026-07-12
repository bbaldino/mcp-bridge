# Generic MCP stdio -> streamable-http bridge, built on Node 22.
#
# Why this exists: the stock `supercorp/supergateway:uvx` image ships Node 20,
# which trips a timing-sensitive race in the streamable-http
# `initialize -> tools/list` handshake (modelcontextprotocol/python-sdk#1675,
# typescript-sdk#530). MCP clients connect fine but load ZERO tools. Node 22
# with supergateway 3.4.3 clears it (verified end-to-end against claude-cli).
#
# Usage: pass the supergateway args as the container command, e.g.
#   --stdio "uvx unraid-mcp" --outputTransport streamableHttp --port 8088 --streamableHttpPath /mcp
# and supply the wrapped server's secrets as environment variables.
FROM node:22-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# uv/uvx, so the bridge can launch Python MCP servers via `uvx <server>`
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Pin the supergateway version we verified on Node 22
RUN npm install -g supergateway@3.4.3

ENTRYPOINT ["supergateway"]

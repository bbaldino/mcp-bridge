"""Front ONE long-lived plex-mcp-server stdio child with streamable HTTP.

plex-mcp-server offers only --transport {stdio,sse}. supergateway, which every
other MCP stack here uses, spawns a fresh stdio child per MCP session — that is
the ~0.39 s every `initialize` was costing. It also cannot bridge the SSE the
server does speak: `sse -> streamableHttp not supported`, verified on both
3.4.3 and the current 4.1.0.

Passing a Client INSTANCE rather than a config dict is the load-bearing detail.
fastmcp then reuses that one session, so a single child lives for the life of
the container. Handing as_proxy a config dict builds a client per request and
puts us straight back to per-session spawning.
"""

import os

from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.client.transports import StdioTransport

client = Client(
    StdioTransport(
        command="plex-mcp-server",
        args=["--transport", "stdio"],
        # PLEX_URL / PLEX_TOKEN reach the child this way.
        env=dict(os.environ),
    )
)

FastMCP.as_proxy(client, name="plex-proxy").run(
    transport="http",
    host=os.environ.get("PROXY_HOST", "0.0.0.0"),
    port=int(os.environ.get("PROXY_PORT", "8087")),
    path=os.environ.get("PROXY_PATH", "/mcp"),
)

# plex-mcp-server behind a streamable-HTTP proxy, as ONE long-lived process.
#
# Why this is a separate image from the supergateway bridge at the repo root:
# supergateway spawns a child per MCP session (~0.39 s per initialize) and
# cannot bridge sse -> streamableHttp in any released version. See proxy.py.
#
# ⚠️ TWO virtualenvs, deliberately. plex-mcp-server pins `mcp==1.26.0` exactly,
# which cannot co-resolve with a current fastmcp — installing both into one env
# fails outright ("your requirements are unsatisfiable"). They never import each
# other; the proxy only needs the `plex-mcp-server` binary on PATH to spawn it.
#
# ⚠️ fastmcp is pinned to 3.x on purpose. `FastMCP.as_proxy` was REMOVED in 4.x
# (verified: absent in 4.0.10, present in 3.0.0 and 3.4.7). Do not "upgrade"
# this to 4 without replacing the proxy mechanism.
#
# Chosen over sparfenyuk/mcp-proxy, which raven proposed: that package's current
# release 0.12.0 is from 2026-05-14 and declares `mcp>=1.17.0` with NO upper
# bound while actually crashing on mcp >= 1.24 ("cannot import name
# 'request_ctx'"). A resolver would happily build a broken image.
FROM python:3.13-slim

# The MCP server, isolated with its exact `mcp` pin.
RUN python -m venv /opt/plex \
 && /opt/plex/bin/pip install --no-cache-dir plex-mcp-server==1.1.7

# The proxy, isolated with its own much newer dependency tree.
RUN python -m venv /opt/proxy \
 && /opt/proxy/bin/pip install --no-cache-dir fastmcp==3.4.7

# Only the server's binary is shared, not its libraries.
ENV PATH="/opt/plex/bin:${PATH}"

COPY proxy.py /opt/proxy.py

# PROXY_PORT / PROXY_PATH / PROXY_HOST override at runtime.
ENTRYPOINT ["/opt/proxy/bin/python", "/opt/proxy.py"]

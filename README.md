# mcp-bridge

A generic **MCP stdio → streamable-http bridge**, built on **Node 22**.

It wraps a stdio-only MCP server (e.g. `uvx unraid-mcp`, `uvx plex-mcp-server`)
with [supergateway](https://github.com/supercorp-ai/supergateway) and exposes it
over streamable-http, so an HTTP-only MCP host (like our caas backend) can reach it.

## Why not the stock `supercorp/supergateway:uvx` image?

That image ships **Node 20**, which trips a timing-sensitive race in the
streamable-http `initialize → tools/list` handshake
([python-sdk#1675](https://github.com/modelcontextprotocol/python-sdk/issues/1675),
[typescript-sdk#530](https://github.com/modelcontextprotocol/typescript-sdk/issues/530)).
The MCP client connects and `initialize` succeeds, but `tools/list` gets dropped —
so the server loads with **zero tools** and silently appears "missing." A plain
`curl` probe (initialize, then a separate tools/list) always passes, which makes
it maddening to diagnose. Rebuilding on **Node 22** clears it; verified 0/5 → 5/5
loading against the real claude-cli.

## Usage

The image's entrypoint is `supergateway`. Pass its args as the container command,
and give the wrapped server its secrets via environment variables.

```bash
docker run -d --name mcp-unraid -p 8088:8088 \
  -e UNRAID_API_URL=http://unraid.home/graphql \
  -e UNRAID_API_KEY=... \
  -e UNRAID_MCP_TRANSPORT=stdio \
  ghcr.io/OWNER/mcp-bridge:latest \
  --stdio "uvx unraid-mcp" --outputTransport streamableHttp --port 8088 --streamableHttpPath /mcp
```

### Unraid "Add Container"

| Field | Value |
|---|---|
| Repository | `ghcr.io/OWNER/mcp-bridge:latest` |
| Port | `8088` → `8088` (TCP) |
| Post Arguments | `--stdio "uvx unraid-mcp" --outputTransport streamableHttp --port 8088 --streamableHttpPath /mcp` |
| Variable | `UNRAID_API_URL` = `http://unraid.home/graphql` |
| Variable | `UNRAID_API_KEY` = `…` |
| Variable | `UNRAID_MCP_TRANSPORT` = `stdio` |

To bridge a different stdio server, change the `--stdio "..."` command and the
port; the image is unchanged.

## GHCR package visibility

The image bakes **no secrets** (they're runtime env), so the published package can
safely be **public** — set the package to Public in its GitHub settings and Unraid
can pull it with no credentials. For a private package, add GHCR registry creds in
Unraid instead.

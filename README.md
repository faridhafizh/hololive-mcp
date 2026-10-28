<div align="center">

# hololive-mcp

**An MCP server that brings hololive talent profiles and news to any AI client.**

[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-2.3.0-6E56CF)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://github.com/faridhafizh/hololive-mcp/pulls)

</div>

---

`hololive-mcp` is a lightweight [Model Context Protocol](https://modelcontextprotocol.io/) server that exposes data from the official [hololive English website](https://hololive.hololivepro.com/en) as tools any MCP-compatible client can call. Ask your AI assistant about a talent's profile, browse the roster, or catch up on the latest announcements — no API key required.

Built with the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) and served over **stdio**.

## Features

- **Three read-only tools** — list the roster, fetch a full talent profile, and read the latest news.
- **No API key, no account** — data is read from the public hololive website.
- **Markdown-ready output** — responses are formatted for direct display in chat.
- **Client agnostic** — works with Claude Desktop, VS Code, Cursor, OpenCode, and any other MCP client that can spawn a stdio process.
- **Small footprint** — `requests`, `beautifulsoup4`, and `lxml`.

## Available Tools

| Tool | Arguments | Description |
| --- | --- | --- |
| `list_talents` | — | Returns every talent listed on the official hololive English site — all generations and branches, including alumni and affiliates — with their English name, Japanese name, and profile slug. |
| `get_talent_profile` | `talent_slug` (string) | Returns a talent's catchphrase, biography, and social links. The slug is the last segment of their profile URL, e.g. `mori-calliope`. |
| `get_recent_news` | — | Returns the 10 most recent items from the hololive English news page as Markdown links. |

### Example output

`list_talents`

```text
- Mori Calliope (森カリオペ) | slug: mori-calliope
- Takanashi Kiara (小鳥遊キアラ) | slug: takanashi-kiara
- Ninomae Ina'nis (一伊那尓栖) | slug: ninomae-inanis
```

`get_talent_profile("mori-calliope")`

```text
**Mori Calliope**
Catchphrase: "Dead Beats, listen up! Your Mori's been working hard for you!"

Biography:
The Grim Reaper's first apprentice...

Social Links:
YouTube: https://www.youtube.com/channel/UCL_qhgtOy0dy1Agp8vkySQg
X: https://twitter.com/moricalliope
```

`get_recent_news`

```text
- [2026.10.19 hololive Meet comes to Sweden...](https://hololive.hololivepro.com/en/news/20261019-01-239/)
- [2026.10.16 hololive 7th fes. delayed screening events...](https://hololive.hololivepro.com/en/news/20261016-01-238/)
```

> Each news entry includes the full article body, not just the headline. Expect long strings.

## Requirements

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** — recommended, but a plain `pip` install also works
- **Node.js 18+** — only needed for the MCP Inspector (`mcp dev`)

## Installation

```bash
git clone https://github.com/faridhafizh/hololive-mcp.git
cd hololive-mcp

# Create the virtual environment and install dependencies
uv sync
```

<details>
<summary>Using pip instead of uv</summary>

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e .
```

</details>

## Usage

### 1. Run the server directly

```bash
uv run hololive-mcp
```

The equivalent entry point for scripts and inspectors is:

```bash
uv run server.py
```

Both start the server on **stdio** and wait for a client. Nothing is printed to `stdout` except MCP messages.

### 2. Debug with the MCP Inspector

```bash
uv run mcp dev server.py
```

This launches a browser UI (usually <http://localhost:6274>) where you can list tools and call them manually. Requires Node.js.

### 3. Connect from Claude Desktop

Add the following to your Claude Desktop config file:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hololive": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\hololive-mcp",
        "run",
        "hololive-mcp"
      ]
    }
  }
}
```

Replace the path with the absolute location of your clone, then restart Claude Desktop.

### 4. Connect from other clients

Any client that supports stdio MCP servers works. Point it at the same command:

```json
{
  "command": "uv",
  "args": ["--directory", "/path/to/hololive-mcp", "run", "hololive-mcp"]
}
```

For example, in VS Code (`.vscode/mcp.json`):

```json
{
  "servers": {
    "hololive": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/path/to/hololive-mcp", "run", "hololive-mcp"]
    }
  }
}
```

## Example prompts

Once connected, try:

- "List every hololive talent and group them by branch."
- "Show me Mori Calliope's profile and social links."
- "Who are the hololive English -Justice- members?"
- "Summarize the three most recent hololive announcements."
- "Which talents have graduated? Give me their names and slugs."

## Project structure

```text
hololive-mcp/
├── src/
│   └── hololive_mcp/
│       ├── __init__.py      # Package entry point (main, mcp)
│       └── server.py        # MCPServer definition and tool implementations
├── server.py                # Convenience shim for `mcp dev server.py`
├── pyproject.toml           # Project metadata and dependencies
├── uv.lock                  # Reproducible dependency lockfile
├── LICENSE
└── README.md
```

## Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| `Could not find the talent list on the page.` | The site markup changed. Update the CSS selectors in `src/hololive_mcp/server.py`. |
| `requests.exceptions.Timeout` | The request exceeded the 15-second timeout. Check your connection and retry. |
| `403 Forbidden` | The default `User-Agent` is being blocked. Update `HEADERS` in `src/hololive_mcp/server.py`. |
| `mcp dev` fails to start | Node.js is missing or too old. Install Node.js 18+. |
| Japanese names show as `??????` in a Windows console | Set `PYTHONIOENCODING=utf-8` before running. MCP clients are unaffected. |

Because the server scrapes HTML, breakage after a site redesign is expected from time to time. Selector fixes are welcome — see [Contributing](#contributing).

## Disclaimer

This is an **unofficial, fan-made project**. It is not affiliated with, endorsed by, or sponsored by [COVER Corporation](https://cover-corp.com/) or hololive production.

- All names, images, text, and other content belong to their respective owners.
- Data is retrieved from the public hololive website for personal, informational use only.
- Please keep request volume reasonable — the server makes one HTTP request per tool call and does not cache. Do not use it for bulk scraping or redistribution.

## Contributing

Issues and pull requests are welcome.

1. Fork the repository and create a branch: `git checkout -b fix/news-selector`
2. Make your change and verify it with `uv run mcp dev server.py`
3. Keep the diff focused, and describe what you tested in the PR

## License

Released under the [MIT License](LICENSE).

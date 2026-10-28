"""Convenience entry point.

Lets `uv run server.py` and `uv run mcp dev server.py` work from the project
root while the actual implementation lives in the installed package.
"""

from hololive_mcp.server import mcp  # noqa: F401

from hololive_mcp import main

if __name__ == "__main__":
    main()

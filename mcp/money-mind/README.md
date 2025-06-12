**Setting up the MCP Server**

uv init money-mind
cd money-mind

uv add "mcp[cli]"
pip install "mcp[cli]"

Run the mcp server
uv run mcp

After developing the server you can head back to the console and do the following command
uv run mcp install server.py
And it responds with - Added server 'money-mind' to Claude config

Restart ClaudeDesktop, don't just close the window.
It would reflect the available MCP Servers only after an Exit


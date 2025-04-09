# MCP Server Scrapli

A basic MCP (Model Context Protocol) Server to interact with network devices using Scrapli.

## 🚀 What's this?

This project is a proof of concept to demonstrate the use of an MCP server by compatible MCP clients (like Claude Desktop) to SSH into network devices. Scrapli was chosen as the connection framework for it's async capabilities.

## 🔧 How to install
> Note: Scrapli is not compatible with Windows operating systems, so this MCP server can only be installed on Linux/MacOS. This guide is for Linux systems only.

This project uses UV for package management.You can install it using pip:
```
pip install uv
```
Alternatively, you can download the installation script using cURL:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
After UV has been installed, clone this repo and install the dependencies using ```uv sync```:
```
git clone https://git.mikelmaeso.com/mmaeso/mcp-server-scrapli.git
cd mcp-server-scrapli
uv sync
```
## 🔧 Starting the server
Activate the virtualenv with:
```
source .venv/bin/activate
```
Rename the ```.env.example``` file to ```.env``` and set your device username and password. Finally, run the server with:
```
uv run main.py
```
By default, the server will listen on ```0.0.0.0``` and port ```8080```, but you can change this behaviour using the ```---host``` and ```--port``` flags, respectively:

```
uv run main.py --host 127.0.0.1 --port 8081
```

## 🔧 Using with Claude Desktop
As of April 2025, Claude Desktop can only use stdio based MCP servers. If you're using Claude Desktop on Windows, the only way to connect it to this MCP server is using an MCP SSE Gateway, like [mcp-server-and-gw](https://github.com/boilingdata/mcp-server-and-gw). Follow the installation instructions and add the following configuration to your ```claude_desktop_config.json``` file:

```
{
  "mcpServers": {
    "Claude Gateway Example": {
      "command": "npx",
      "args": [
        "mcp-server-and-gw", "http://<hostname-of-mcp-server>:<port>/"
      ]
    }
  }
}
```

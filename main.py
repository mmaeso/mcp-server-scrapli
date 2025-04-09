from scrapli import AsyncScrapli
from typing import List, Any
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
from dotenv import load_dotenv
import uvicorn
import json
import os


load_dotenv(".env")

mcp = FastMCP("mcp-server-scrapli")


def connect_device(hostname: str,platform: str):
    device = dict(
        host=hostname,
        platform=platform,
        auth_username=os.environ.get("AUTH_USERNAME"),
        auth_password=os.environ.get("AUTH_PASSWORD"),
        auth_strict_key=False,
        transport="asyncssh"
        )
    return AsyncScrapli(**device)


@mcp.tool()
async def send_command(hostname: str,platform: str, command: str) -> str:
    """Send a single command to a network device and return the output.

    Args:
        hostname (str): Device hostname or IP address
        platform (str): Platform of the device (e.g., "cisco_iosxe")
        command (str): Command to execute on the device

    Returns:
        str: The output of the command execution

    Raises:
        ScrapliException: If there is an error connecting to the device or executing the command
    """
    conn = connect_device(hostname, platform)
    async with conn:
        response = await conn.send_command(command)
    return response.result


@mcp.tool()
async def send_config(hostname: str,platform: str, command: str) -> str:
    """Send a single configuration command (e.g., "interface GigabitEthernet0/0" or "router ospf 1")
    to a network device and return the output.

    Args:
        hostname (str): Device hostname or IP address
        platform (str): Platform of the device (e.g., "cisco_iosxe")
        command (str): Configuration command to execute on the device

    Returns:
        str: The output of the command execution

    Raises:
        ScrapliException: If there is an error connecting to the device or executing the command
    """
    conn = connect_device(hostname, platform)
    async with conn:
        response = await conn.send_config(command)
    return response


@mcp.tool()
async def send_configs(hostname: str,platform: str, commands: List[str]) -> str:
    """Send multiple configuration commands that are not global commands 
    (e.g., ["interface GigabitEthernet0/0", "ip address 192.168.1.1 255.255.255"] 
    or ["router bgp 65000","bgp router-id 192.168.1.1"])
    to a network device and return the output.


    Args:
        hostname (str): Device hostname or IP address
        platform (str): Platform of the device (e.g., "cisco_iosxe")
        commands List[str]: List of configuration commands to execute on the device

    Returns:
        str: The output of the command execution

    Raises:
        ScrapliException: If there is an error connecting to the device or executing the command
    """
    conn = connect_device(hostname, platform)
    async with conn:
        response = await conn.send_configs(commands)
    return response

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse
    
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)

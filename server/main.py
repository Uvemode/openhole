import os
import subprocess

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from zellij import send_message

load_dotenv()

ZELLIJ_SESSION = os.getenv("ZELLIJ_SESSION", "claude")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "3000"))

mcp = FastMCP("claude-proxy", host=HOST, port=PORT)


@mcp.tool()
def send_to_claude(message: str) -> str:
    """
    Send an anonymized message to the Claude Code session running in Zellij.
    The message must have all sensitive values replaced with tokens before calling this tool.
    """
    try:
        send_message(ZELLIJ_SESSION, message)
        return "Message delivered to Claude Code session."
    except subprocess.CalledProcessError as e:
        return f"Failed to deliver message: {e.stderr.decode().strip()}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

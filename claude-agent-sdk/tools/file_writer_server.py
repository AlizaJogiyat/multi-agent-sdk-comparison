"""MCP tool server for writing files to disk."""

from claude_agent_sdk import tool, create_sdk_mcp_server

import json
import os


@tool(
    "write_file",
    "Write content to a file on disk. Creates directories if needed.",
    {"path": str, "content": str},
)
async def write_file(args):
    """Write content to a file."""
    path = args["path"]
    content = args["content"]
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return {
            "content": [
                {"type": "text", "text": json.dumps({"status": "success", "path": os.path.abspath(path), "bytes_written": len(content)})}
            ]
        }
    except Exception as e:
        return {"content": [{"type": "text", "text": json.dumps({"status": "error", "error": str(e)})}]}


def create_file_writer_server():
    return create_sdk_mcp_server(
        name="file_writer",
        version="1.0.0",
        tools=[write_file],
    )

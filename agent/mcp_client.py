#connect to MCP-Project over stdio
import os

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()


class MCPClient:
    def __init__(self):
        self.python_path = os.getenv("MCP_PYTHON_PATH")
        self.server_path = os.getenv("MCP_SERVER_PATH")

        if not self.python_path:
            raise ValueError("MCP_PYTHON_PATH is not set in .env")

        if not self.server_path:
            raise ValueError("MCP_SERVER_PATH is not set in .env")

        self.session = None
        self.stdio_context = None

    async def connect(self):
        server_params = StdioServerParameters(
            command=self.python_path,
            args=[self.server_path],
        )

        self.stdio_context = stdio_client(server_params)

        read, write = await self.stdio_context.__aenter__()

        self.session = ClientSession(read, write)
        await self.session.__aenter__()

        await self.session.initialize()

        tools = await self.session.list_tools()

        print("Connected to MCP server.")
        print("Available tools:")

        for tool in tools.tools:
            print(f"- {tool.name}")

        return tools.tools

    async def call_tool(self, tool_name, arguments):
        if self.session is None:
            raise RuntimeError("MCP client is not connected.")

        result = await self.session.call_tool(
            tool_name,
            arguments=arguments,
        )

        return result

    async def close(self):
        if self.session is not None:
            await self.session.__aexit__(None, None, None)
            self.session = None

        if self.stdio_context is not None:
            await self.stdio_context.__aexit__(None, None, None)
            self.stdio_context = None
         

'''Test Section'''          
# import asyncio

# async def test():
#     client = MCPClient()

#     try:
#         await client.connect()
#     finally:
#         await client.close()


# if __name__ == "__main__":
#     asyncio.run(test())
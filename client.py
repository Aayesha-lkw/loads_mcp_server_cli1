import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    # Connect to a streamable HTTP server
    async with streamablehttp_client("https://optloadserver-direct-b3-222121553030.europe-west1.run.app/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        # Create a session using the client streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            # List available tools
            tools = await session.list_tools()
            tool_name = [tool.name for tool in tools.tools][0]
            #print(f"Available tools: {[tool.name for tool in tools.tools]}")
            result = await session.call_tool(tool_name, {"end_lat": 45, "end_lon": 10, "end_time": "2025-10-13T00:00:00Z", "start_lat": 51.87, "start_lon": 12.58, "start_time": "2025-10-05T00:00:00Z"})
            #print(result.content[1].text)
            full_result = []
            for i in range (len(result.content)):
                full_result.append(result.content[i].text)
            print(full_result)

if __name__ == "__main__":
    asyncio.run(main())
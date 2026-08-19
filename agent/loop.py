import asyncio
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from agent.mcp_client import MCPClient
from agent.hitl import is_write_tool, confirm_tool_call
from agent.prompts import SYSTEM_PROMPT


load_dotenv()

MODEL = "gpt-4o-mini"

def convert_mcp_tools_to_openai_tools(mcp_tools):
    tools = []

    for tool in mcp_tools:
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                },
            }
        )

    return tools


async def run_agent(
    mcp,
    openai_client,
    messages,
    openai_tools,
    tool_trace=None,
):
    
    while True:

        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
        )

        message = response.choices[0].message

        # No tool call -> return normal answer
        if not message.tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                }
            )

            return message.content

        # Save assistant's tool request
        messages.append(message)

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            # Record tool call for evaluation
            if tool_trace is not None:
                tool_trace.append(tool_name)

            try:
                arguments = json.loads(
                    tool_call.function.arguments
                )
            except json.JSONDecodeError:
                arguments = {}

            print(f"\nAgent wants to call: {tool_name}")
            print(f"Arguments: {arguments}")

            # -------------------------
            # HITL for write operations
            # -------------------------
            if is_write_tool(tool_name):

                approved = confirm_tool_call(
                    tool_name,
                    arguments,
                )

                if not approved:

                    tool_result = {
                        "error": "User declined the write operation."
                    }

                    print("Write cancelled.")

                else:

                    result = await mcp.call_tool(
                        tool_name,
                        arguments,
                    )

                    tool_result = result.model_dump()

            # -------------------------
            # Read-only operations
            # -------------------------
            else:

                result = await mcp.call_tool(
                    tool_name,
                    arguments,
                )

                tool_result = result.model_dump()

            # Send MCP result back to LLM
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )


async def main():

    print("HR Assistant")
    print("Type 'exit' to quit.")

    # OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set in .env"
        )

    openai_client = OpenAI(api_key=api_key)

    # MCP connection stays open
    mcp = MCPClient()

    try:
        # Connect ONCE
        mcp_tools = await mcp.connect()

        openai_tools = convert_mcp_tools_to_openai_tools(
            mcp_tools
        )

        # Conversation history
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        while True:
            user_message = input("\nYou: ").strip()

            if user_message.lower() == "exit":
                break

            if not user_message:
                continue

            # Add user message to conversation
            messages.append(
                {
                    "role": "user",
                    "content": user_message,
                }
            )

            try:
                answer = await run_agent(
                    mcp,
                    openai_client,
                    messages,
                    openai_tools,
                )

                print(f"\nAssistant: {answer}")

            except Exception as e:
                print(f"\nError: {e}")

    finally:
        await mcp.close()


if __name__ == "__main__":
    asyncio.run(main())
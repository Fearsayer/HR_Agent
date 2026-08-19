# HITL_AUTO_APPROVE=true python -m evals.run_evals

import asyncio
import os
import sys
import yaml
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

from agent.mcp_client import MCPClient
from agent.loop import convert_mcp_tools_to_openai_tools, run_agent
from agent.prompts import SYSTEM_PROMPT


load_dotenv()

MODEL = "gpt-4o-mini"


def load_cases():
    with open("evals/cases.yaml", "r") as file:
        data = yaml.safe_load(file)

    return data["cases"]


def check_case(case, tool_trace, answer):
    expected_tools = case.get("expected_tools", [])
    forbidden_tools = case.get("forbidden_tools", [])

    for tool in expected_tools:
        if tool not in tool_trace:
            return False, f"Missing expected tool: {tool}"

    for tool in forbidden_tools:
        if tool in tool_trace:
            return False, f"Forbidden tool was used: {tool}"

    return True, "Passed"


async def run_case(
    case,
    mcp,
    openai_client,
    openai_tools,
):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": case["prompt"],
        },
    ]

    tool_trace = []

    try:
        answer = await run_agent(
            mcp,
            openai_client,
            messages,
            openai_tools,
            tool_trace,
        )

        passed, reason = check_case(
            case,
            tool_trace,
            answer,
        )

        return {
            "id": case["id"],
            "passed": passed,
            "tools": tool_trace,
            "reason": reason,
            "answer": answer,
        }

    except Exception as e:

        return {
            "id": case["id"],
            "passed": False,
            "tools": tool_trace,
            "reason": f"Exception: {e}",
            "answer": "",
        }


def write_report(results):
    passed_count = sum(
        result["passed"]
        for result in results
    )

    total_count = len(results)

    with open("evals/report.md", "a") as file:

        file.write("\n\n---\n\n")
        file.write("# Evaluation Run\n\n")

        file.write(
            f"- Timestamp: `{datetime.now().astimezone().isoformat()}`\n"
        )
        file.write(f"- Model: `{MODEL}`\n")
        file.write(f"- Cases: `{total_count}`\n")
        file.write(f"- Passed: `{passed_count}`\n")
        file.write(
            f"- Pass rate: `{passed_count / total_count:.1%}`\n"
        )
        file.write(
            "- Command: "
            "`HITL_AUTO_APPROVE=true python -m evals.run_evals`\n\n"
        )

        file.write("## Results\n\n")

        file.write("| Case | Result | Tools | Reason |\n")
        file.write("|---|---|---|---|\n")

        for result in results:

            status = "PASS" if result["passed"] else "FAIL"
            tools = ", ".join(result["tools"])

            file.write(
                f"| {result['id']} "
                f"| {status} "
                f"| `{tools}` "
                f"| {result['reason']} |\n"
            )

        file.write("\n## Failure Notes\n\n")

        failures = [
            result
            for result in results
            if not result["passed"]
        ]

        if not failures:
            file.write("All evaluation cases passed.\n")
        else:
            for result in failures:
                file.write(
                    f"- **{result['id']}**: "
                    f"{result['reason']}\n"
                )


async def main():

    cases = load_cases()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set in .env"
        )

    openai_client = OpenAI(
        api_key=api_key
    )

    mcp = MCPClient()

    try:

        mcp_tools = await mcp.connect()

        openai_tools = convert_mcp_tools_to_openai_tools(
            mcp_tools
        )

        results = []

        for case in cases:

            print(
                f"\nRunning {case['id']}: "
                f"{case['description']}"
            )

            result = await run_case(
                case,
                mcp,
                openai_client,
                openai_tools,
            )

            results.append(result)

            status = "PASS" if result["passed"] else "FAIL"

            print(f"{status}")
            print(f"Tools: {result['tools']}")
            print(f"Reason: {result['reason']}")

        passed_count = sum(
            result["passed"]
            for result in results
        )

        print(
            f"\n{passed_count}/{len(results)} cases passed."
        )

        # Save this run to report.md
        write_report(results)

        print("Report saved to evals/report.md")

        if passed_count != len(results):
            sys.exit(1)

    finally:

        await mcp.close()


if __name__ == "__main__":
    asyncio.run(main())

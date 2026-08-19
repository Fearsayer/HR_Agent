# confirm writes before execution
import os

WRITE_TOOLS = {
    "create_employee",
    "update_employee",
    "deactivate_employee",
}


def is_write_tool(tool_name):
    return tool_name in WRITE_TOOLS


def confirm_tool_call(tool_name, arguments):
    print("Human confirmation required.")
    print(f"Tool: {tool_name}")
    print("Arguments:")

    for key, value in arguments.items():
        print(f"  {key}: {value}")
    
    # for run_evals.py
    if os.getenv("HITL_AUTO_APPROVE") == "true":
        print(f"HITL auto-approved: {tool_name}")
        return True

    answer = input("\nProceed? [y/N]: ").strip().lower()

    return answer == "y"
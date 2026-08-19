# Evaluation Run

- Timestamp: `2026-08-19T19:10:14.003434+08:00`
- Model: `gpt-4o-mini`
- Cases: `8`
- Passed: `7`
- Pass rate: `87.5%`
- Command: `HITL_AUTO_APPROVE=true python -m evals.run_evals`

## Results

| Case | Result | Tools | Reason |
|---|---|---|---|
| F1 | PASS | `list_employees` | Passed |
| F2 | PASS | `get_employee` | Passed |
| F3 | PASS | `create_employee` | Passed |
| F4 | PASS | `get_org_summary, get_org_summary` | Passed |
| F5 | PASS | `get_employee` | Passed |
| F6 | FAIL | `` | Missing expected tool: get_employee |
| F7 | PASS | `deactivate_employee` | Passed |
| F8 | PASS | `update_employee` | Passed |

## Failure Notes

- **F6**: Missing expected tool: get_employee


---

# Evaluation Run

- Timestamp: `2026-08-19T19:12:48.151270+08:00`
- Model: `gpt-4o-mini`
- Cases: `8`
- Passed: `8`
- Pass rate: `100.0%`
- Command: `HITL_AUTO_APPROVE=true python -m evals.run_evals`

## Results

| Case | Result | Tools | Reason |
|---|---|---|---|
| F1 | PASS | `list_employees` | Passed |
| F2 | PASS | `get_employee` | Passed |
| F3 | PASS | `create_employee` | Passed |
| F4 | PASS | `get_org_summary, get_org_summary` | Passed |
| F5 | PASS | `get_employee` | Passed |
| F6 | PASS | `get_employee` | Passed |
| F7 | PASS | `deactivate_employee` | Passed |
| F8 | PASS | `update_employee` | Passed |

## Failure Notes

All evaluation cases passed.

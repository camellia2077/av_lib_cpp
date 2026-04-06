---
trigger: always_on
---

[CONSTRAINTS]

- Shell / encoding:
  - Use `pwsh` (PowerShell 7.5.4) as the default shell entry for command execution.

[BUILD_AND_TEST_AFTER_CHANGES]

- After any code change, the agent must run compile and tests before finishing.
- Use project Python entrypoint only: `tools/script/run.py`.

- Required verification sequence:
  1. Compile:
     - `python tools/script/run.py build --mode fast`
  2. Core C++ tests:
     - `python tools/script/run.py test-core`
  3. End-to-end smoke test (CLI flow):
     - `python tools/script/run.py smoke-cli`

- Pass criteria:
  - All commands above exit with code `0`.
  - No skipped step unless explicitly approved by the user.

- Reporting requirements:
  - In the final response, report:
    - Which commands were executed.
    - Whether each command passed or failed.
    - If a step failed, include the failure reason and the next fix action.

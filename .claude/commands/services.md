Manage app services (frontend, LangGraph backend, ADK/Gemini backend) using the Makefile.

Parse the user's request and run the correct make target from the project root.

## Target map

| Intent | Target |
|---|---|
| start / up everything | `make up` |
| stop / down everything | `make down` |
| restart everything | `make restart` |
| start frontend | `make up-frontend` |
| stop frontend | `make down-frontend` |
| restart frontend | `make restart-frontend` |
| start langgraph / default backend | `make up-langgraph` |
| stop langgraph | `make down-langgraph` |
| restart langgraph | `make restart-langgraph` |
| start adk / gemini backend | `make up-adk` |
| stop adk | `make down-adk` |
| restart adk | `make restart-adk` |
| start both backends | `make up-backends` |
| stop both backends | `make down-backends` |
| restart both backends | `make restart-backends` |
| show logs | `make logs` |
| check status / what's running | `make status` |

## Rules
- Always run from the project root (where the Makefile lives).
- If the intent is ambiguous, run `make status` first, then ask the user to clarify.
- After running, show the command output to the user.

!cd /Users/umairahmed.khan/workspace/talabat-workspace/generative-ui-app && make $ARGS

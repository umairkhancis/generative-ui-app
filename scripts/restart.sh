#!/usr/bin/env bash
# restart.sh — kill all app processes and restart frontend + both backends
# Usage: ./restart.sh
# Runs in: generative-ui-app root

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
LOG_DIR="$ROOT/scripts/.logs"

mkdir -p "$LOG_DIR"

# ── 1. Kill existing processes on all app ports ────────────────────────────────
echo "🔴 Stopping existing processes..."
for port in 8000 8009 4002 5173; do
  pids=$(lsof -ti:"$port" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "  Killing port $port (PIDs: $pids)"
    echo "$pids" | xargs kill -9 2>/dev/null || true
  fi
done
sleep 1

# ── 2. Start LangGraph backend (:8000) ────────────────────────────────────────
echo "🟢 Starting LangGraph backend on :8000..."
"$BACKEND/.venv/bin/python" "$BACKEND/main_langgraph.py" \
  > "$LOG_DIR/langgraph.log" 2>&1 &
LANGGRAPH_PID=$!
echo "  PID: $LANGGRAPH_PID  →  logs: $LOG_DIR/langgraph.log"

# ── 3. Start ADK backend (:8009) ──────────────────────────────────────────────
echo "🟢 Starting ADK backend on :8009..."
"$BACKEND/.venv/bin/python" "$BACKEND/main_adk.py" \
  > "$LOG_DIR/adk.log" 2>&1 &
ADK_PID=$!
echo "  PID: $ADK_PID  →  logs: $LOG_DIR/adk.log"

# ── 4. Start Frontend (CopilotKit :4002 + Vite :5173) ─────────────────────────
echo "🟢 Starting frontend (runtime :4002 + Vite :5173)..."
cd "$FRONTEND"
npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "  PID: $FRONTEND_PID  →  logs: $LOG_DIR/frontend.log"

# ── 5. Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "✅ All services started. PIDs saved to $LOG_DIR/pids.txt"
echo "$LANGGRAPH_PID $ADK_PID $FRONTEND_PID" > "$LOG_DIR/pids.txt"

echo ""
echo "  Service          Port   Log"
echo "  ─────────────────────────────────────────────────"
echo "  LangGraph        8000   $LOG_DIR/langgraph.log"
echo "  ADK/Gemini       8009   $LOG_DIR/adk.log"
echo "  CopilotKit       4002   $LOG_DIR/frontend.log"
echo "  Vite (React)     5173   $LOG_DIR/frontend.log"
echo ""
echo "  Tail all logs:  tail -f $LOG_DIR/*.log"
echo "  Kill all:       kill \$(cat $LOG_DIR/pids.txt)"

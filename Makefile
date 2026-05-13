# Makefile — generative-ui-app
# Manages LangGraph (:8000) and Frontend (:4002/:5173)
#
# Usage:
#   make up              — start all services
#   make down            — stop all services
#   make restart         — stop then start all services
#   make up-frontend     — start frontend only
#   make down-frontend   — stop frontend only
#   make restart-frontend
#   make up-langgraph    — start LangGraph backend only
#   make down-langgraph  — stop LangGraph backend only
#   make restart-langgraph
#   make logs            — tail all logs
#   make status          — show which ports are in use
#   make clean           — remove node_modules, .venv, build artifacts, logs
#   make clean-frontend  — remove frontend node_modules, .vite, dist
#   make clean-backend   — remove backend .venv, __pycache__, .pyc files
#   make install         — install all dependencies (frontend + backend)
#   make install-frontend — npm install in frontend/
#   make install-backend  — create .venv and pip install -r requirements.txt

ROOT        := $(shell pwd)
BACKEND     := $(ROOT)/backend
FRONTEND    := $(ROOT)/frontend
LOG_DIR     := $(ROOT)/scripts/.logs

PORTS_ALL       := 8000 4002 5173
PORTS_LANGGRAPH := 8000
PORTS_FRONTEND  := 4002 5173

.PHONY: up down restart \
        up-frontend down-frontend restart-frontend \
        up-langgraph down-langgraph restart-langgraph \
        logs status \
        install install-frontend install-backend \
        clean clean-frontend clean-backend

# ── Helpers ───────────────────────────────────────────────────────────────────

$(LOG_DIR):
	@mkdir -p $(LOG_DIR)

define kill-ports
	@for port in $(1); do \
	  pids=$$(lsof -ti:$$port 2>/dev/null || true); \
	  if [ -n "$$pids" ]; then \
	    echo "  🔴 Killing port $$port (PIDs: $$pids)"; \
	    echo "$$pids" | xargs kill -9 2>/dev/null || true; \
	  fi; \
	done
endef

# ── ALL ───────────────────────────────────────────────────────────────────────

up: $(LOG_DIR) up-langgraph up-frontend
	@echo ""
	@echo "✅ All services up."
	@echo "   LangGraph  :8000  →  $(LOG_DIR)/langgraph.log"
	@echo "   Frontend   :4002/:5173  →  $(LOG_DIR)/frontend.log"
	@echo ""
	@echo "   Tail logs:  make logs"

down:
	@echo "🔴 Stopping all services..."
	$(call kill-ports,$(PORTS_ALL))
	@sleep 1
	@echo "✅ All services stopped."

restart: down up

# ── FRONTEND ──────────────────────────────────────────────────────────────────

up-frontend: $(LOG_DIR)
	@echo "🟢 Starting frontend (CopilotKit :4002 + Vite :5173)..."
	@cd $(FRONTEND) && npm run dev > $(LOG_DIR)/frontend.log 2>&1 & \
	  echo $$! > $(LOG_DIR)/frontend.pid; \
	  echo "   PID: $$(cat $(LOG_DIR)/frontend.pid)  →  $(LOG_DIR)/frontend.log"

down-frontend:
	@echo "🔴 Stopping frontend..."
	$(call kill-ports,$(PORTS_FRONTEND))
	@echo "✅ Frontend stopped."

restart-frontend: down-frontend up-frontend

# ── LANGGRAPH ─────────────────────────────────────────────────────────────────

up-langgraph: $(LOG_DIR)
	@echo "🟢 Starting LangGraph backend (:8000)..."
	@$(BACKEND)/.venv/bin/python -u $(BACKEND)/main_langgraph.py \
	  > $(LOG_DIR)/langgraph.log 2>&1 & \
	  echo $$! > $(LOG_DIR)/langgraph.pid; \
	  echo "   PID: $$(cat $(LOG_DIR)/langgraph.pid)  →  $(LOG_DIR)/langgraph.log"

down-langgraph:
	@echo "🔴 Stopping LangGraph..."
	$(call kill-ports,$(PORTS_LANGGRAPH))
	@echo "✅ LangGraph stopped."

restart-langgraph: down-langgraph up-langgraph

# ── UTILS ─────────────────────────────────────────────────────────────────────

logs:
	@tail -f $(LOG_DIR)/*.log

# ── INSTALL ───────────────────────────────────────────────────────────────────

install: install-frontend install-backend
	@echo "✅ All dependencies installed."

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	@cd $(FRONTEND) && npm install
	@echo "✅ Frontend dependencies installed."

install-backend:
	@echo "📦 Installing backend dependencies..."
	@python3.12 -m venv $(BACKEND)/.venv
	@$(BACKEND)/.venv/bin/pip install --upgrade pip -q
	@$(BACKEND)/.venv/bin/pip install -r $(BACKEND)/requirements.txt
	@echo "✅ Backend dependencies installed."

# ── CLEAN ─────────────────────────────────────────────────────────────────────

clean: clean-frontend clean-backend
	@rm -rf $(LOG_DIR)
	@echo "🧹 All clean."

clean-frontend:
	@echo "🧹 Cleaning frontend..."
	@rm -rf $(FRONTEND)/node_modules $(FRONTEND)/.vite $(FRONTEND)/dist
	@echo "   Removed: node_modules, .vite, dist"

clean-backend:
	@echo "🧹 Cleaning backend..."
	@rm -rf $(BACKEND)/.venv $(BACKEND)/__pycache__ $(BACKEND)/*.pyc
	@find $(BACKEND) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "   Removed: .venv, __pycache__, .pyc files"

status:
	@echo "Port status:"
	@for port in $(PORTS_ALL); do \
	  pids=$$(lsof -ti:$$port 2>/dev/null || true); \
	  if [ -n "$$pids" ]; then \
	    echo "  ✅ :$$port  (PIDs: $$pids)"; \
	  else \
	    echo "  ❌ :$$port  (not running)"; \
	  fi; \
	done

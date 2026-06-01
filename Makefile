.PHONY: help venv install install-backend install-frontend backend frontend dev test stop check-ports

BACKEND_DIR := backend
FRONTEND_DIR := frontend
VENV_BIN := .venv/bin
BACKEND_PORT := 8000
FRONTEND_PORT := 5173
UVICORN := $(VENV_BIN)/uvicorn app.main:app --reload --host 127.0.0.1 --port $(BACKEND_PORT)

help:
	@echo "CareerPilot AI — available commands:"
	@echo ""
	@echo "  make venv             Create backend/.venv (Python virtualenv)"
	@echo "  make install          Install backend + frontend dependencies"
	@echo "  make install-backend  Create venv + pip install backend"
	@echo "  make install-frontend Install frontend npm packages"
	@echo "  make backend          Run FastAPI on http://127.0.0.1:$(BACKEND_PORT)"
	@echo "  make frontend         Run Vite on http://127.0.0.1:$(FRONTEND_PORT)"
	@echo "  make dev              Stop stale servers, then run backend + frontend"
	@echo "  make stop             Free ports $(BACKEND_PORT) and $(FRONTEND_PORT)"
	@echo "  make test             Run backend tests (uses backend/.venv)"
	@echo ""

venv:
	@test -d $(BACKEND_DIR)/$(VENV_BIN) || python3 -m venv $(BACKEND_DIR)/.venv
	@echo "Backend venv ready at $(BACKEND_DIR)/.venv"

install: install-backend install-frontend

install-backend: venv
	cd $(BACKEND_DIR) && $(VENV_BIN)/pip install --upgrade pip
	cd $(BACKEND_DIR) && $(VENV_BIN)/pip install -e ".[dev]"

install-frontend:
	cd $(FRONTEND_DIR) && npm install

# Free dev ports — only kills processes LISTENING (not browser/IDE clients)
stop:
	@echo "Stopping dev servers on ports $(BACKEND_PORT), $(FRONTEND_PORT), 5174..."
	@for port in $(BACKEND_PORT) $(FRONTEND_PORT) 5174; do \
		pids=$$(lsof -tiTCP:$$port -sTCP:LISTEN 2>/dev/null); \
		if [ -n "$$pids" ]; then \
			echo "  port $$port -> PID $$pids"; \
			kill $$pids 2>/dev/null || true; \
			sleep 0.3; \
			pids=$$(lsof -tiTCP:$$port -sTCP:LISTEN 2>/dev/null); \
			if [ -n "$$pids" ]; then kill -9 $$pids 2>/dev/null || true; fi; \
		fi; \
	done
	@echo "Ports cleared."

check-ports:
	@for port in $(BACKEND_PORT) $(FRONTEND_PORT); do \
		if lsof -tiTCP:$$port -sTCP:LISTEN >/dev/null 2>&1; then \
			echo "ERROR: Port $$port is still in use. Run 'make stop' or quit the other app."; \
			exit 1; \
		fi; \
	done

backend: venv check-ports
	cd $(BACKEND_DIR) && $(UVICORN)

frontend: check-ports
	cd $(FRONTEND_DIR) && npm run dev

# Stop stale servers first, then start both
dev: venv stop
	@sleep 0.5
	@$(MAKE) check-ports --no-print-directory
	@echo "Starting backend (:$(BACKEND_PORT)) + frontend (:$(FRONTEND_PORT))..."
	@trap 'kill 0' INT TERM; \
	(cd $(BACKEND_DIR) && $(UVICORN)) & \
	(cd $(FRONTEND_DIR) && npm run dev) & \
	wait

test: venv
	cd $(BACKEND_DIR) && $(VENV_BIN)/python -m pytest tests/ -q

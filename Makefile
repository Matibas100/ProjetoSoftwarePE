.PHONY: db-status db-up db-baseline db-reconcile test-unit test-integration test-backend test-frontend test-coverage test test-e2e

db-status:
	python backend/database/migrate.py status

db-up:
	python backend/database/migrate.py up

db-baseline:
	python backend/database/migrate.py baseline --confirm

db-reconcile:
	python backend/database/migrate.py reconcile $(VERSION) --confirm

test-unit:
	python backend/tests/run_unit.py
	npm run test:unit

test-integration:
	python backend/tests/run_integration.py

test-backend:
	python backend/tests/run_backend_coverage.py

test-frontend:
	npm run test:coverage

test-coverage: test-backend test-frontend

test: test-coverage

test-e2e:
	python scripts/run_e2e.py

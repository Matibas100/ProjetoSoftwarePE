.PHONY: test-unit test-integration test-backend test-frontend test-coverage test

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

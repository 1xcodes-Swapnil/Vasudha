#!/usr/bin/env bash
set -e

echo "=== Running Backend Pytest Suite ==="
python3 -m pytest backend/tests -v

echo "=== Running Frontend Typecheck & Lint ==="
npm run lint

echo "=== Running Frontend Build Check ==="
npm run build

echo "=== All Phase 0 Checks Passed Successfully ==="

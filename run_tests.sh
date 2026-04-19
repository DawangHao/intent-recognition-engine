#!/bin/bash

# 运行所有测试
echo "Running all tests..."
pytest -v

# 运行特定类型的测试
echo "\nRunning unit tests..."
pytest tests/unit/ -v

echo "\nRunning integration tests..."
pytest tests/integration/ -v

echo "\nRunning end-to-end tests..."
pytest tests/e2e/ -v
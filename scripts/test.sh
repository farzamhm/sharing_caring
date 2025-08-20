#!/bin/bash

# Test runner script for the food sharing platform

set -e

echo "🧪 Running Food Sharing Platform Tests"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
COVERAGE_MIN=80
TEST_TYPE="all"
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --coverage-min)
            COVERAGE_MIN="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit              Run only unit tests"
            echo "  --integration       Run only integration tests"
            echo "  --coverage-min N    Set minimum coverage percentage (default: 80)"
            echo "  --verbose, -v       Verbose output"
            echo "  --help, -h          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${RED}❌ pytest not found. Installing test dependencies...${NC}"
    pip install -r requirements.txt
fi

# Create test reports directory
mkdir -p reports

# Set test command based on type
PYTEST_CMD="pytest"
case $TEST_TYPE in
    "unit")
        PYTEST_CMD="$PYTEST_CMD tests/unit/"
        echo -e "${YELLOW}🔬 Running Unit Tests${NC}"
        ;;
    "integration")
        PYTEST_CMD="$PYTEST_CMD tests/integration/"
        echo -e "${YELLOW}🔗 Running Integration Tests${NC}"
        ;;
    "all")
        echo -e "${YELLOW}🚀 Running All Tests${NC}"
        ;;
esac

# Add coverage and reporting options
PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=term-missing --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml --cov-fail-under=$COVERAGE_MIN --junit-xml=reports/junit.xml"

if [[ -n "$VERBOSE" ]]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

echo "Running: $PYTEST_CMD"
echo ""

# Run tests
if $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "📊 Test Reports:"
    echo "  • Coverage Report: reports/coverage/index.html"
    echo "  • JUnit XML: reports/junit.xml"
    
    # Show coverage summary
    if command -v coverage &> /dev/null; then
        echo ""
        echo "📈 Coverage Summary:"
        coverage report --skip-covered
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}❌ Some tests failed!${NC}"
    
    # Show failed tests summary if available
    if [ -f "reports/junit.xml" ]; then
        echo ""
        echo "📋 Failed Tests Summary:"
        python -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('reports/junit.xml')
    root = tree.getroot()
    for testcase in root.iter('testcase'):
        failure = testcase.find('failure')
        error = testcase.find('error')
        if failure is not None or error is not None:
            print(f'  • {testcase.get(\"classname\")}.{testcase.get(\"name\")}')
except Exception:
    pass
        "
    fi
    
    exit 1
fi
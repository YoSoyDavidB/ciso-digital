#!/bin/bash
# =============================================================================
# CISO Digital - Quality Verification Script
# =============================================================================
#
# Este script ejecuta todos los checks de calidad del proyecto:
# - Tests con pytest y coverage
# - Linting con ruff
# - Formatting con black
# - Type checking con mypy
#
# Exit codes:
#   0 - Todos los checks pasaron
#   1 - Al menos un check falló
#
# Usage:
#   ./scripts/verify.sh
#

set -e  # Exit on error

# =============================================================================
# Configuration
# =============================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Coverage mínimo requerido
MIN_COVERAGE=80

# Contadores
CHECKS_PASSED=0
CHECKS_FAILED=0
TOTAL_CHECKS=5

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# =============================================================================
# Main Script
# =============================================================================

print_header "🔍 CISO Digital - Quality Verification"

print_info "Starting quality checks..."
print_info "Minimum coverage required: ${MIN_COVERAGE}%"
echo ""

# Cambiar al directorio backend
cd "$(dirname "$0")/.." || exit 1

# Verificar que estamos en el directorio correcto
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Are you in the backend directory?"
    exit 1
fi

# Verificar que el venv existe (buscar .venv o venv)
if [ -d ".venv" ]; then
    VENV_DIR=".venv"
elif [ -d "venv" ]; then
    VENV_DIR="venv"
else
    print_error "Virtual environment not found at .venv/ or venv/"
    print_info "Run: python -m venv .venv && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt"
    exit 1
fi

# Activar venv (detectar Windows o Unix)
if [ -f "${VENV_DIR}/Scripts/python.exe" ]; then
    # Windows
    PYTHON="${VENV_DIR}/Scripts/python.exe"
    PYTEST="${VENV_DIR}/Scripts/pytest"
    BLACK="${VENV_DIR}/Scripts/black"
    RUFF="${VENV_DIR}/Scripts/ruff"
    MYPY="${VENV_DIR}/Scripts/mypy"
else
    # Unix/Linux/Mac
    PYTHON="${VENV_DIR}/bin/python"
    PYTEST="${VENV_DIR}/bin/pytest"
    BLACK="${VENV_DIR}/bin/black"
    RUFF="${VENV_DIR}/bin/ruff"
    MYPY="${VENV_DIR}/bin/mypy"
fi

# =============================================================================
# Check 1: Tests con Coverage
# =============================================================================

print_header "1️⃣  Running Tests with Coverage"

if $PYTEST --cov=app --cov-report=term --cov-report=html -v; then
    print_success "All tests passed"
    print_info "Coverage report generated in htmlcov/"
    ((CHECKS_PASSED++))
else
    print_error "Tests failed"
    ((CHECKS_FAILED++))
fi

# =============================================================================
# Check 2: Black (Code Formatting)
# =============================================================================

print_header "2️⃣  Checking Code Formatting (Black)"

if $BLACK --check app/ tests/; then
    print_success "Code formatting is correct"
    ((CHECKS_PASSED++))
else
    print_error "Code formatting issues found"
    print_info "Run: .venv/bin/black app/ tests/"
    ((CHECKS_FAILED++))
fi

# =============================================================================
# Check 3: Ruff (Linting)
# =============================================================================

print_header "3️⃣  Running Linter (Ruff)"

if $RUFF check app/ tests/; then
    print_success "No linting errors found"
    ((CHECKS_PASSED++))
else
    print_error "Linting errors found"
    print_info "Run: .venv/bin/ruff check --fix app/ tests/"
    ((CHECKS_FAILED++))
fi

# =============================================================================
# Check 4: Ruff Format Check
# =============================================================================

print_header "4️⃣  Checking Ruff Formatting"

if $RUFF format --check app/ tests/; then
    print_success "Ruff formatting is correct"
    ((CHECKS_PASSED++))
else
    print_error "Ruff formatting issues found"
    print_info "Run: .venv/bin/ruff format app/ tests/"
    ((CHECKS_FAILED++))
fi

# =============================================================================
# Check 5: Mypy (Type Checking)
# =============================================================================

print_header "5️⃣  Running Type Checker (Mypy)"

if $MYPY app/; then
    print_success "No type errors found"
    ((CHECKS_PASSED++))
else
    print_error "Type checking errors found"
    print_info "Review type hints in your code"
    ((CHECKS_FAILED++))
fi

# =============================================================================
# Summary
# =============================================================================

print_header "📊 Verification Summary"

echo ""
echo "Total checks: $TOTAL_CHECKS"
echo -e "${GREEN}Passed: $CHECKS_PASSED${NC}"
echo -e "${RED}Failed: $CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    print_success "All quality checks passed! 🎉"
    echo ""
    print_info "Your code is ready for commit."
    echo ""
    exit 0
else
    print_error "$CHECKS_FAILED check(s) failed"
    echo ""
    print_warning "Please fix the issues above before committing."
    echo ""
    exit 1
fi

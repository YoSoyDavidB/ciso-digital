#!/bin/bash
# Script para probar la API de CISO Digital

set -e

echo "🚀 Testing CISO Digital API..."
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URL base
BASE_URL="http://localhost:8000"

echo -e "${BLUE}1. Testing Root Endpoint (/)${NC}"
curl -s ${BASE_URL}/ | python3 -m json.tool
echo ""

echo -e "${BLUE}2. Testing Health Check (/health)${NC}"
curl -s ${BASE_URL}/health | python3 -m json.tool
echo ""

echo -e "${BLUE}3. Testing Detailed Health Check (/health/detailed)${NC}"
curl -s ${BASE_URL}/health/detailed | python3 -m json.tool
echo ""

echo -e "${GREEN}✅ All endpoints working!${NC}"
echo ""
echo "📖 Documentation available at:"
echo "   - Swagger UI: ${BASE_URL}/docs"
echo "   - ReDoc:      ${BASE_URL}/redoc"
echo "   - OpenAPI:    ${BASE_URL}/openapi.json"

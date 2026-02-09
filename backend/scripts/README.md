# Scripts de Desarrollo

Este directorio contiene scripts útiles para desarrollo, demos y verificación de calidad.

## 📋 Scripts Disponibles

### 🎭 `demo_ciso_orchestrator.py` - Demo del Sistema

**Demostración completa del orchestrador y respuesta a incidentes.**

**Uso:**
```bash
cd backend
python scripts/demo_ciso_orchestrator.py
```

**Funcionalidades demostradas:**
1. **Conversación multi-turno con memoria**
   - Query 1: "¿Cuáles son los riesgos críticos?"
   - Query 2: "Dame más detalles del primer riesgo"
   - Verifica que mantiene contexto entre mensajes

2. **Clasificación de intenciones**
   - Queries de riesgo → RiskAssessmentAgent
   - Queries de incidentes → IncidentResponseAgent  
   - Queries de compliance → ComplianceAgent
   - Muestra confidence scores y agente seleccionado

3. **Respuesta a incidentes completa**
   - Detección de ransomware
   - Clasificación automática (tipo, severidad, confidence)
   - Generación de plan de respuesta
   - Acciones inmediatas y contención
   - Notificaciones a stakeholders
   - Métricas de rendimiento

**Output esperado:**
```
🤖 CISO Digital Demo - Orchestrator & Incident Response

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test 1: Multi-turn Conversation with Memory
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 User: ¿Cuáles son los riesgos críticos?
🔍 Orchestrator: Intent: risk_assessment (confidence: 0.95)
                Agent: RiskAssessmentAgent
🤖 CISO: [respuesta detallada con 3 riesgos críticos]
...
```

### `verify.sh` - Verificación de Calidad

Script principal que ejecuta todos los checks de calidad del proyecto.

**Uso:**
```bash
cd backend
./scripts/verify.sh
```

**Checks ejecutados:**

1. **Tests con Coverage** - `pytest --cov`
   - Ejecuta todos los tests unitarios, integración y e2e
   - Genera reporte de coverage en `htmlcov/`
   - Verifica que todos los tests pasen

2. **Formatting (Black)** - `black --check`
   - Verifica que el código esté formateado correctamente
   - Si falla: `black app/ tests/`

3. **Linting (Ruff)** - `ruff check`
   - Verifica errores de linting y PEP8
   - Si falla: `ruff check --fix app/ tests/`

4. **Formatting (Ruff)** - `ruff format --check`
   - Verifica formato con ruff
   - Si falla: `ruff format app/ tests/`

5. **Type Checking (Mypy)** - `mypy app/`
   - Verifica type hints y type safety
   - Si falla: revisar type hints en el código

**Exit codes:**
- `0` - Todos los checks pasaron ✅
- `1` - Al menos un check falló ❌

**Output:**
- Imprime resultados coloreados en terminal
- Muestra resumen final con estadísticas
- Indica qué hacer si algún check falla

---

### `test_api.sh` - Prueba de API

Script para probar los endpoints de la API.

**Uso:**
```bash
# 1. Iniciar el servidor en otra terminal
cd backend
.venv/bin/uvicorn app.main:app --reload

# 2. Ejecutar tests
./scripts/test_api.sh
```

**Endpoints probados:**
- `GET /` - Root endpoint
- `GET /health` - Health check básico
- `GET /health/detailed` - Health check detallado

---

## 🔧 Configuración

Los scripts requieren que el virtual environment esté configurado en `.venv/`:

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
```

---

## 📝 Uso en CI/CD

El script `verify.sh` está diseñado para usarse en pipelines de CI/CD:

```yaml
# GitHub Actions example
- name: Run quality checks
  run: |
    cd backend
    ./scripts/verify.sh
```

```yaml
# GitLab CI example
test:
  script:
    - cd backend
    - ./scripts/verify.sh
```

---

## 🎯 Pre-commit Hook

Puedes configurar el script para ejecutarse automáticamente antes de cada commit:

```bash
# .git/hooks/pre-commit
#!/bin/bash
cd backend && ./scripts/verify.sh
```

O usar `pre-commit` framework (recomendado):
```bash
cd backend
pre-commit install
```

---

## 🐛 Troubleshooting

### Error: "Virtual environment not found"
```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
```

### Error: "pytest: command not found"
```bash
.venv/bin/pip install -r requirements-dev.txt
```

### Tests fallan
```bash
# Ver detalles completos
.venv/bin/pytest -vv

# Ver output de prints
.venv/bin/pytest -s

# Ejecutar test específico
.venv/bin/pytest tests/unit/test_services/test_risk_calculator.py -v
```

### Formateo incorrecto
```bash
# Aplicar formato automáticamente
.venv/bin/black app/ tests/
.venv/bin/ruff format app/ tests/
```

### Errores de linting
```bash
# Aplicar fixes automáticos
.venv/bin/ruff check --fix app/ tests/
```

---

**Última actualización:** Febrero 2026  
**Mantenedor:** Equipo CISO Digital

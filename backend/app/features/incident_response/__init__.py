"""
Incident Response Feature Module.

Este módulo implementa la funcionalidad completa de respuesta a incidentes
de seguridad, incluyendo:

- Modelos de base de datos para incidentes
- Servicios de gestión de incidentes
- Schemas de validación
- Integración con IncidentResponseAgent

Flujo típico de un incidente:
1. Detección (DETECTED)
2. Investigación (INVESTIGATING)
3. Contención (CONTAINED)
4. Erradicación (ERADICATED)
5. Recuperación (RECOVERED)
6. Cierre (CLOSED)
"""

__version__ = "0.1.0"

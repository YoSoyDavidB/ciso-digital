"""
Shared Exceptions - Excepciones Personalizadas
==============================================

Excepciones personalizadas de la aplicación que proporcionan
mejor contexto y manejo de errores.

Contenido esperado:
- CISOBaseException     → Excepción base de la aplicación
- NotFoundError         → Recurso no encontrado (404)
- ValidationError       → Error de validación (422)
- AuthenticationError   → Error de autenticación (401)
- AuthorizationError    → Error de autorización (403)
- DatabaseError         → Error de base de datos (500)
- ExternalServiceError  → Error de servicio externo (502)

Ejemplo de uso:
    from app.shared.exceptions import NotFoundError

    async def get_risk(risk_id: str) -> Risk:
        risk = await db.get(Risk, risk_id)
        if not risk:
            raise NotFoundError(f"Risk {risk_id} not found")
        return risk
"""

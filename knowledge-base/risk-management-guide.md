# Guía de Gestión de Riesgos de Seguridad de la Información

## Resumen Ejecutivo

La gestión de riesgos de seguridad de la información es un proceso sistemático para identificar, evaluar y tratar riesgos que pueden afectar la confidencialidad, integridad y disponibilidad de los activos de información de una organización. Esta guía proporciona un marco práctico basado en estándares internacionales (ISO 27005, NIST RMF, FAIR) para implementar un programa efectivo de gestión de riesgos.

Un programa de gestión de riesgos efectivo permite a las organizaciones tomar decisiones informadas sobre inversiones en seguridad, priorizar recursos, cumplir con requisitos regulatorios y mantener un nivel de riesgo aceptable alineado con los objetivos de negocio.

## ¿Qué es la Gestión de Riesgos de Seguridad?

La gestión de riesgos de seguridad de la información es el proceso coordinado de dirigir y controlar una organización respecto a los riesgos de seguridad de la información. Implica la aplicación sistemática de políticas, procedimientos y prácticas para identificar, analizar, evaluar, tratar, monitorear y comunicar riesgos.

### Conceptos Fundamentales

**Riesgo**: Efecto de la incertidumbre sobre los objetivos. En seguridad de la información:
- **Riesgo = Amenaza × Vulnerabilidad × Impacto**
- O alternativamente: **Riesgo = Probabilidad × Impacto**

**Activo**: Cualquier cosa que tiene valor para la organización (datos, sistemas, aplicaciones, personal, reputación).

**Amenaza**: Causa potencial de un incidente no deseado que puede resultar en daño a un sistema o la organización.

**Vulnerabilidad**: Debilidad de un activo o control que puede ser explotada por una o más amenazas.

**Impacto**: Consecuencia de un evento que afecta los objetivos de la organización.

**Control**: Medida que modifica el riesgo (preventivo, detectivo, correctivo).

## Objetivos de la Gestión de Riesgos

1. **Identificación Proactiva**: Identificar riesgos antes de que se materialicen
2. **Priorización Efectiva**: Enfocar recursos en los riesgos más críticos
3. **Decisiones Informadas**: Proporcionar información para decisiones de inversión en seguridad
4. **Cumplimiento**: Satisfacer requisitos regulatorios y contractuales
5. **Optimización de Recursos**: Maximizar ROI en controles de seguridad
6. **Cultura de Riesgo**: Desarrollar conciencia y responsabilidad sobre riesgos en toda la organización
7. **Resiliencia**: Mejorar capacidad de prevenir, detectar y recuperarse de incidentes

## Proceso de Gestión de Riesgos

### Fase 1: Establecimiento del Contexto

**Objetivo**: Definir alcance, criterios y estructura del proceso de gestión de riesgos.

#### Actividades Clave:

1. **Definir Alcance**
   - ¿Qué áreas de la organización están incluidas?
   - ¿Qué procesos de negocio se consideran?
   - ¿Qué sistemas y tecnologías están en alcance?
   - Límites geográficos y temporales

2. **Identificar Criterios de Riesgo**
   - Criterios de impacto (financiero, reputacional, operacional, legal)
   - Niveles de probabilidad
   - Niveles de riesgo aceptable (apetito de riesgo)
   - Matriz de riesgo (probabilidad × impacto)

3. **Identificar Partes Interesadas**
   - Alta dirección
   - Propietarios de procesos de negocio
   - Equipo de seguridad/TI
   - Auditoría interna
   - Legal y cumplimiento
   - Recursos humanos

4. **Definir Roles y Responsabilidades**
   - Risk Owner (propietario del riesgo)
   - Risk Manager (gestor de riesgo)
   - Control Owner (propietario del control)
   - Risk Committee (comité de riesgos)

**Entregables**:
- Plan de gestión de riesgos
- Criterios de evaluación de riesgos
- Matriz de riesgo
- Registro de partes interesadas
- Documento RACI (Responsible, Accountable, Consulted, Informed)

### Fase 2: Identificación de Riesgos

**Objetivo**: Identificar qué puede pasar, cómo y por qué.

#### Metodologías de Identificación:

**1. Inventario de Activos**
```
Categorías de activos:
- Información (bases de datos, documentos, código fuente)
- Software (aplicaciones, sistemas operativos)
- Hardware (servidores, workstations, dispositivos móviles)
- Servicios (cloud, comunicaciones, energía)
- Personas (empleados, contratistas, terceros)
- Instalaciones (oficinas, centros de datos)
- Intangibles (reputación, propiedad intelectual)
```

**2. Identificación de Amenazas**

Amenazas Intencionales:
- Ciberataques (ransomware, phishing, DDoS)
- Insider malicioso (empleado descontento)
- Espionaje corporativo/estatal
- Hacktivismo
- Crimen organizado

Amenazas Accidentales:
- Error humano (configuración incorrecta, borrado accidental)
- Fallo de software (bugs, crashes)
- Fallo de hardware (discos, servidores)

Amenazas Ambientales:
- Desastres naturales (incendio, inundación, terremoto)
- Fallo de infraestructura (energía, refrigeración, comunicaciones)
- Pandemia/emergencias sanitarias

**3. Identificación de Vulnerabilidades**

Técnicas:
- Escaneo de vulnerabilidades (Nessus, Qualys, OpenVAS)
- Revisión de configuraciones (benchmarks CIS)
- Pruebas de penetración
- Revisión de código (SAST, DAST)
- Auditorías de seguridad
- Análisis de logs y eventos

Categorías:
- Vulnerabilidades técnicas (CVE)
- Vulnerabilidades de proceso (falta de procedimientos)
- Vulnerabilidades físicas (controles de acceso débiles)
- Vulnerabilidades humanas (falta de capacitación)

**4. Escenarios de Riesgo**

Formato recomendado:
```
ID: RISK-001
Título: Ransomware en servidor de base de datos
Activo: Base de datos de clientes (CRM)
Amenaza: Ransomware
Vulnerabilidad: Servidor sin parchear, sin backups offline
Escenario: Un atacante explota vulnerabilidad no parcheada para 
           desplegar ransomware que encripta base de datos de clientes
Causa raíz: Falta de gestión de parches, backups inadecuados
```

**Entregables**:
- Inventario de activos con valoración
- Catálogo de amenazas
- Registro de vulnerabilidades
- Registro de riesgos (inicial)

### Fase 3: Análisis de Riesgos

**Objetivo**: Comprender la naturaleza del riesgo y determinar el nivel de riesgo.

#### Métodos de Análisis

**Análisis Cualitativo**

Escala de Probabilidad:
```
1 - Muy Baja: < 5% probabilidad anual (una vez cada 20+ años)
2 - Baja: 5-25% probabilidad anual (una vez cada 4-20 años)
3 - Media: 25-50% probabilidad anual (una vez cada 2-4 años)
4 - Alta: 50-75% probabilidad anual (una vez cada 1-2 años)
5 - Muy Alta: > 75% probabilidad anual (múltiples veces al año)
```

Escala de Impacto:
```
1 - Insignificante: < $10K, sin interrupción, sin impacto reputacional
2 - Menor: $10K-$100K, interrupción < 4 horas, impacto reputacional mínimo
3 - Moderado: $100K-$1M, interrupción < 24 horas, impacto reputacional local
4 - Mayor: $1M-$10M, interrupción < 1 semana, impacto reputacional nacional
5 - Severo: > $10M, interrupción > 1 semana, impacto reputacional global
```

Matriz de Riesgo (Probabilidad × Impacto):
```
         │ 1-Insig │ 2-Menor │ 3-Moder │ 4-Mayor │ 5-Severo
─────────┼─────────┼─────────┼─────────┼─────────┼──────────
5-Muy Alta│    5    │   10    │   15    │   20    │    25
4-Alta    │    4    │    8    │   12    │   16    │    20
3-Media   │    3    │    6    │    9    │   12    │    15
2-Baja    │    2    │    4    │    6    │    8    │    10
1-Muy Baja│    1    │    2    │    3    │    4    │    5

Nivel de Riesgo:
- 1-5: Bajo (Verde)
- 6-12: Medio (Amarillo)
- 15-20: Alto (Naranja)
- 25: Crítico (Rojo)
```

**Análisis Cuantitativo**

**Método ALE (Annual Loss Expectancy)**:
```
SLE (Single Loss Expectancy) = Valor del Activo × Factor de Exposición
ALE = SLE × ARO (Annual Rate of Occurrence)

Ejemplo:
- Activo: Base de datos de clientes = $5,000,000
- Factor de Exposición: 80% (destrucción parcial)
- SLE = $5,000,000 × 0.80 = $4,000,000
- ARO = 0.25 (una vez cada 4 años)
- ALE = $4,000,000 × 0.25 = $1,000,000/año
```

**Método FAIR (Factor Analysis of Information Risk)**:
```
Risk = Probable Loss Event Frequency × Probable Loss Magnitude

LEF = Threat Event Frequency × Vulnerability
Loss Magnitude = Primary Loss + Secondary Loss

Ejemplo avanzado usando distribuciones de probabilidad
para análisis Monte Carlo
```

**Riesgo Inherente vs. Residual**

- **Riesgo Inherente**: Riesgo sin considerar controles existentes
- **Riesgo Residual**: Riesgo después de aplicar controles existentes
- **Riesgo Objetivo**: Nivel de riesgo deseado después de tratamiento

```
Riesgo Residual = Riesgo Inherente - Efectividad de Controles

Ejemplo:
- Riesgo Inherente: 20 (Alto)
- Controles existentes reducen riesgo en 70%
- Riesgo Residual: 20 × 0.30 = 6 (Medio)
```

**Entregables**:
- Registro de riesgos actualizado con niveles de riesgo
- Matriz de riesgos visual
- Análisis de brechas de control
- Mapa de calor de riesgos (heat map)

### Fase 4: Evaluación de Riesgos

**Objetivo**: Comparar riesgos con criterios de aceptación y priorizar.

#### Actividades:

1. **Comparar con Apetito de Riesgo**
   - ¿El riesgo residual está dentro del apetito de riesgo?
   - ¿Qué riesgos exceden el umbral de aceptación?

2. **Priorización**
   ```
   Prioridad = (Nivel de Riesgo × Peso de Impacto) + Factor de Urgencia
   
   Considerar:
   - Requisitos regulatorios (compliance urgente)
   - Amenazas emergentes (0-days, nuevos malware)
   - Contexto de negocio (lanzamientos, adquisiciones)
   - Interdependencias (riesgos relacionados)
   ```

3. **Categorización**
   - Riesgos críticos: Requieren acción inmediata
   - Riesgos altos: Requieren acción en 30-90 días
   - Riesgos medios: Requieren acción en 3-6 meses
   - Riesgos bajos: Monitorear

**Entregables**:
- Lista priorizada de riesgos
- Riesgos que requieren decisión de tratamiento
- Riesgos aceptables sin tratamiento adicional

### Fase 5: Tratamiento de Riesgos

**Objetivo**: Seleccionar e implementar opciones para modificar riesgos.

#### Opciones de Tratamiento

**1. Modificar el Riesgo (Mitigación)**

Estrategias:
- **Reducir Probabilidad**: Implementar controles preventivos
  - Firewall, antivirus, IDS/IPS
  - Gestión de parches
  - Capacitación de usuarios
  - MFA (autenticación multifactor)
  
- **Reducir Impacto**: Implementar controles detectivos/correctivos
  - Backups y recuperación
  - Cifrado de datos
  - Segmentación de red
  - Plan de respuesta a incidentes

Ejemplo de Plan de Tratamiento:
```
ID: RISK-001
Riesgo: Ransomware en servidor de base de datos
Nivel Actual: 20 (Alto)
Nivel Objetivo: 6 (Medio)

Controles a Implementar:
1. Implementar gestión automática de parches (reduce probabilidad)
   - Responsable: Equipo de TI
   - Costo: $15,000
   - Plazo: 60 días
   - Reducción esperada: 40%

2. Implementar backups offline inmutables (reduce impacto)
   - Responsable: Equipo de Backups
   - Costo: $25,000
   - Plazo: 30 días
   - Reducción esperada: 60%

3. Implementar EDR en todos los servidores (detecta y responde)
   - Responsable: Equipo de Seguridad
   - Costo: $30,000/año
   - Plazo: 45 días
   - Reducción esperada: 50%

Riesgo Residual Esperado: 20 × (0.6 × 0.4 × 0.5) = 2.4 ≈ 3 (Bajo)
Inversión Total: $70,000 inicial + $30,000/año
ROI: Evitar pérdida potencial de $1M/año
```

**2. Retener el Riesgo (Aceptación)**

Cuándo aceptar:
- Costo de mitigación > costo de la pérdida potencial
- Riesgo dentro del apetito de riesgo
- No hay controles efectivos disponibles
- Riesgo necesario para objetivos de negocio

Requiere:
- Aprobación formal de la alta dirección
- Documentación de justificación
- Monitoreo continuo
- Revisión periódica

**3. Evitar el Riesgo**

Estrategias:
- Descontinuar actividad riesgosa
- No entrar en nuevo mercado/tecnología riesgosa
- Retirar sistema vulnerable
- Cambiar proceso de negocio

Ejemplo:
```
Riesgo: Uso de software EOL (End of Life) sin soporte
Tratamiento: Migrar a versión soportada o reemplazar sistema
Resultado: Riesgo eliminado completamente
```

**4. Compartir el Riesgo (Transferencia)**

Mecanismos:
- **Seguro cibernético**: Transferir impacto financiero
  - Cobertura típica: $1M-$10M
  - Costo: 1-3% de cobertura anualmente
  - Incluye: ransomware, brechas de datos, BI

- **Contratos con terceros**: Cláusulas de responsabilidad
  - SLAs con proveedores cloud
  - Indemnizaciones de proveedores
  - Requisitos de seguridad contractuales

- **Outsourcing**: Transferir operación riesgosa
  - SOC as a Service
  - Managed Security Services
  - Cloud providers (responsabilidad compartida)

**Entregables**:
- Plan de tratamiento de riesgos
- Presupuesto de controles
- Cronograma de implementación
- Decisiones de aceptación de riesgo (formales)
- Riesgos residuales documentados

### Fase 6: Monitoreo y Revisión

**Objetivo**: Asegurar que el programa de gestión de riesgos sigue siendo efectivo.

#### Actividades de Monitoreo

**1. Monitoreo de Controles**
```
Métricas de efectividad de controles:
- % de sistemas parcheados en SLA
- Tiempo promedio de detección de incidentes
- Tasa de falsos positivos de controles
- Cobertura de controles (% de activos protegidos)
- Disponibilidad de controles críticos
```

**2. Monitoreo de Riesgos**
```
KRIs (Key Risk Indicators):
- Número de vulnerabilidades críticas no remediadas
- Edad promedio de vulnerabilidades abiertas
- Número de incidentes de seguridad por mes
- % de usuarios que fallan simulacros de phishing
- Tiempo de última evaluación de riesgos
```

**3. Revisiones Periódicas**

**Revisión Continua** (mensual):
- Nuevas vulnerabilidades (CVE)
- Nuevas amenazas (threat intelligence)
- Cambios en activos
- Efectividad de controles

**Revisión Formal** (trimestral):
- Actualización de registro de riesgos
- Progreso en planes de tratamiento
- Riesgos emergentes
- Presentación a comité de riesgos

**Reevaluación Completa** (anual o cuando):
- Cambios significativos en organización
- Nuevos sistemas o procesos críticos
- Después de incidente mayor
- Cambios regulatorios
- Cambios en apetito de riesgo

**4. Comunicación y Reporte**

**Audiencias y Formato**:

Para Alta Dirección (Executive Dashboard):
```
- Top 5 riesgos críticos
- Mapa de calor de riesgos
- Tendencias de riesgos (mejorando/empeorando)
- Inversión en controles vs. reducción de riesgo
- Estado de cumplimiento regulatorio
- Incidentes significativos del período
```

Para Comité de Riesgos (Risk Committee):
```
- Registro completo de riesgos
- Análisis detallado de riesgos principales
- Planes de tratamiento y progreso
- Nuevos riesgos identificados
- Controles implementados
- Métricas y KRIs
```

Para Equipos Operacionales:
```
- Riesgos relevantes a su área
- Controles bajo su responsabilidad
- Acciones requeridas
- Plazos y prioridades
```

**Entregables**:
- Dashboards de riesgos
- Reportes mensuales/trimestrales
- Alertas de riesgos emergentes
- Recomendaciones de tratamiento

## Frameworks y Metodologías

### ISO 27005:2022

**Características**:
- Estándar internacional para gestión de riesgos de seguridad de la información
- Complementa ISO 27001
- Flexible, no prescriptivo
- Proceso iterativo

**Fases**: Establecimiento de contexto → Identificación → Análisis → Evaluación → Tratamiento → Monitoreo

**Ventajas**:
- Reconocimiento internacional
- Integración con ISO 27001
- Enfoque sistemático

**Desventajas**:
- Requiere interpretación
- Puede ser complejo para organizaciones pequeñas

### NIST Risk Management Framework (RMF)

**Características**:
- Framework del gobierno de USA (NIST SP 800-37)
- Enfoque en sistemas de información
- 7 pasos estructurados
- Integrado con controles NIST SP 800-53

**Pasos**:
1. Prepare (Preparar)
2. Categorize (Categorizar sistemas)
3. Select (Seleccionar controles)
4. Implement (Implementar controles)
5. Assess (Evaluar controles)
6. Authorize (Autorizar sistema)
7. Monitor (Monitorear continuamente)

**Ventajas**:
- Muy detallado y estructurado
- Catálogo extenso de controles
- Ampliamente adoptado en sector público

**Desventajas**:
- Puede ser pesado para sector privado
- Orientado a sistemas federales USA

### FAIR (Factor Analysis of Information Risk)

**Características**:
- Metodología cuantitativa
- Enfoque en pérdida financiera
- Basado en taxonomía estándar
- Usa análisis Monte Carlo

**Componentes**:
```
Risk = Loss Event Frequency × Loss Magnitude

Loss Event Frequency = Threat Event Frequency × Vulnerability
Loss Magnitude = Primary Loss + Secondary Loss
```

**Ventajas**:
- Resultados cuantitativos ($$)
- Facilita decisiones de inversión
- Comunicación efectiva con ejecutivos

**Desventajas**:
- Requiere datos históricos
- Curva de aprendizaje
- Herramientas especializadas costosas

### OCTAVE (Operationally Critical Threat, Asset, and Vulnerability Evaluation)

**Características**:
- Desarrollado por SEI/CMU
- Auto-dirigido (menos consultores)
- Enfoque en activos críticos
- Tres variantes: OCTAVE, OCTAVE-S (small), OCTAVE Allegro

**Fases**:
1. Identificar activos críticos
2. Identificar amenazas a activos
3. Desarrollar estrategias de protección

**Ventajas**:
- Apropiado para self-assessment
- Enfoque en criticidad de negocio
- Workshops colaborativos

**Desventajas**:
- Menos estructura que ISO/NIST
- Requiere compromiso significativo de tiempo

## Mejores Prácticas

### 1. Involucrar al Negocio
- **No es solo un ejercicio de TI**: Gestión de riesgos debe liderar el negocio
- Identificar propietarios de riesgos en áreas de negocio
- Usar lenguaje de negocio, no solo técnico
- Vincular riesgos a objetivos estratégicos

### 2. Mantener Simplicidad
- No sobre-complicar el proceso
- Usar herramientas apropiadas al tamaño de la organización
- Evitar análisis parálisis
- Enfocarse en riesgos materiales

### 3. Ser Pragmático
- "Perfecto es enemigo de bueno"
- Mejor análisis cualitativo simple que cuantitativo complejo sin datos
- Iterar y mejorar con el tiempo
- Quick wins para demostrar valor

### 4. Automatizar Donde Sea Posible
```
Herramientas GRC (Governance, Risk, Compliance):
- RSA Archer
- ServiceNow GRC
- LogicManager
- OneTrust
- Resolver
- SimpleRisk (open source)

Funcionalidades clave:
- Registro de riesgos centralizado
- Workflows de aprobación
- Dashboards y reportes
- Integración con escaneo de vulnerabilidades
- Gestión de controles
```

### 5. Integrar con Otros Procesos
- **Gestión de Proyectos**: Incluir evaluación de riesgos en proyectos
- **Gestión de Cambios**: Evaluar riesgos de cambios
- **Gestión de Incidentes**: Aprender de incidentes para mejorar evaluaciones
- **Auditoría**: Coordinar con auditorías internas/externas
- **Cumplimiento**: Alinear con requisitos regulatorios

### 6. Desarrollar Cultura de Riesgo
- Capacitación regular en gestión de riesgos
- Comunicar importancia desde la alta dirección
- Recompensar identificación proactiva de riesgos
- Evitar "shoot the messenger" cuando se reportan riesgos
- Hacer gestión de riesgos parte de la descripción de todos los puestos

### 7. Cuantificar Cuando Sea Posible
```
Beneficios de cuantificación:
- Facilita decisiones de inversión
- Comunica efectivamente con CFO/CEO
- Permite análisis costo-beneficio de controles
- Priorización objetiva

Ejemplo de análisis ROI de control:
Control: Implementar EDR en todos los endpoints
Costo: $50,000 inicial + $30,000/año
Reducción de riesgo: ALE de $500,000 → $100,000
Ahorro anual: $400,000
ROI primer año: ($400K - $80K) / $80K = 400%
Payback period: ~2.4 meses
```

### 8. Documentar Decisiones
- Registrar todas las decisiones de tratamiento
- Documentar suposiciones y limitaciones
- Mantener trazabilidad
- Facilitar auditorías
- Proteger a la organización legalmente

### 9. Revisar y Actualizar Regularmente
- Riesgos no son estáticos
- Nuevas amenazas emergen constantemente
- Tecnología y negocio cambian
- Controles se degradan con el tiempo
- Establecer calendario de revisiones

### 10. Medir Efectividad del Programa
```
Métricas del programa de gestión de riesgos:
- % de riesgos identificados con tratamiento definido
- Tiempo promedio de remediación de riesgos altos
- % de riesgos fuera de apetito de riesgo
- Cobertura de evaluación (% de activos críticos evaluados)
- Frecuencia de actualizaciones de registro de riesgos
- Satisfacción de stakeholders con proceso
- Reducción de incidentes año sobre año
```

## Herramientas y Recursos

### Herramientas de Evaluación de Riesgos

**Comerciales**:
- **RSA Archer**: Suite completa GRC, altamente configurable
- **ServiceNow GRC**: Integrado con ITSM, flujos automatizados
- **LogicManager**: Fácil de usar, bueno para medianas empresas
- **MetricStream**: Enfoque en cumplimiento y riesgos
- **RiskLens**: Especializado en FAIR, análisis cuantitativo

**Open Source/Gratuitas**:
- **SimpleRisk**: Open source, básico pero funcional
- **OWASP Risk Rating Methodology**: Para riesgos de aplicaciones
- **Excel/Google Sheets**: Plantillas personalizadas (adecuado para SMBs)

### Herramientas de Escaneo de Vulnerabilidades

- **Nessus Professional**: $4,000-$5,000/año
- **Qualys VMDR**: ~$2,000-$4,000/año
- **Rapid7 InsightVM**: ~$2,500-$5,000/año
- **OpenVAS**: Open source, gratuito
- **Tenable.io**: Cloud-based, ~$3,000+/año

### Recursos de Threat Intelligence

**Comerciales**:
- **Recorded Future**: $50K-$200K/año
- **Mandiant Threat Intelligence**: $100K+/año
- **CrowdStrike Falcon Intelligence**: $50K+/año

**Gratuitos**:
- **CISA Known Exploited Vulnerabilities (KEV)**: kev.cisa.gov
- **NVD (National Vulnerability Database)**: nvd.nist.gov
- **MITRE ATT&CK**: attack.mitre.org
- **AlienVault OTX**: otx.alienvault.com
- **CERT/CC Vulnerability Notes**: kb.cert.org

### Estándares y Guías

- **ISO/IEC 27005:2022**: Information security risk management
- **NIST SP 800-30**: Guide for Conducting Risk Assessments
- **NIST SP 800-37**: Risk Management Framework
- **ENISA**: European Union Agency for Cybersecurity guidelines
- **FAIR Institute**: www.fairinstitute.org
- **ISACA Risk IT Framework**: www.isaca.org

## Errores Comunes a Evitar

### 1. Evaluación de Riesgos como Ejercicio de "Check the Box"
- **Problema**: Hacer evaluación solo para cumplimiento, sin uso real
- **Solución**: Integrar en decisiones reales de negocio y seguridad

### 2. Evaluaciones Demasiado Infrecuentes
- **Problema**: Evaluación anual que queda obsoleta rápidamente
- **Solución**: Monitoreo continuo + reevaluaciones cuando cambios significativos

### 3. Falta de Propietarios de Riesgo
- **Problema**: Riesgos asignados a "TI" genéricamente
- **Solución**: Asignar propietario específico con autoridad y recursos

### 4. Análisis Sin Acción
- **Problema**: Identificar muchos riesgos pero no tratarlos
- **Solución**: Priorizar, presupuestar y ejecutar planes de tratamiento

### 5. Enfoque Solo en Riesgos Técnicos
- **Problema**: Ignorar riesgos de personas, procesos, terceros
- **Solución**: Evaluación holística de todos los tipos de riesgos

### 6. Subestimar Riesgos de Terceros
- **Problema**: No evaluar riesgos de proveedores y socios
- **Solución**: Programa formal de gestión de riesgos de terceros (TPRM)

### 7. Falta de Contexto de Negocio
- **Problema**: Evaluar riesgos técnicamente sin impacto de negocio
- **Solución**: Vincular todo riesgo a impacto en objetivos de negocio

### 8. No Comunicar Efectivamente
- **Problema**: Reportes técnicos que ejecutivos no entienden
- **Solución**: Adaptar comunicación a audiencia, usar visualizaciones

## Plantilla de Registro de Riesgos

```
┌─────────────────────────────────────────────────────────────────────┐
│                      REGISTRO DE RIESGOS                            │
├─────────────────────────────────────────────────────────────────────┤
│ ID: RISK-001                                                        │
│ Fecha Identificación: 2026-02-05                                    │
│ Última Actualización: 2026-02-05                                    │
│ Estado: Abierto                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ DESCRIPCIÓN DEL RIESGO                                              │
├─────────────────────────────────────────────────────────────────────┤
│ Título: Ransomware en servidor de base de datos de clientes        │
│                                                                     │
│ Descripción: Un atacante podría explotar vulnerabilidades no       │
│ parcheadas en el servidor de base de datos de CRM para desplegar   │
│ ransomware, encriptar datos de clientes y exigir rescate.          │
│                                                                     │
│ Activo Afectado: Servidor CRM-DB-01 (Base de datos SQL Server)     │
│ Valor del Activo: $5,000,000                                       │
│ Categoría: Ciberseguridad - Malware                                │
├─────────────────────────────────────────────────────────────────────┤
│ ANÁLISIS DE RIESGO                                                  │
├─────────────────────────────────────────────────────────────────────┤
│ Amenaza: Ransomware / Ciberdelincuentes                            │
│ Vulnerabilidad: Servidor 45 días sin parchear, backups en          │
│                 misma red (no offline/inmutables)                   │
│                                                                     │
│ Riesgo Inherente:                                                   │
│   Probabilidad: 4 (Alta - ocurre ~1 vez cada 1-2 años)            │
│   Impacto: 5 (Severo - pérdida $5M+, downtime 1+ semana)          │
│   Nivel: 20 (CRÍTICO) 🔴                                           │
│                                                                     │
│ Controles Existentes:                                               │
│   - Firewall perimetral (efectividad: 30%)                         │
│   - Antivirus básico (efectividad: 20%)                            │
│   - Backups diarios online (efectividad: 40% contra ransomware)    │
│                                                                     │
│ Riesgo Residual:                                                    │
│   Probabilidad: 3 (Media)                                          │
│   Impacto: 4 (Mayor - backups permiten recuperación parcial)       │
│   Nivel: 12 (ALTO) 🟠                                              │
├─────────────────────────────────────────────────────────────────────┤
│ TRATAMIENTO                                                         │
├─────────────────────────────────────────────────────────────────────┤
│ Opción Seleccionada: Modificar (Mitigar)                           │
│ Decisión por: Juan Pérez, CISO                                     │
│ Fecha Decisión: 2026-02-05                                          │
│                                                                     │
│ Plan de Acción:                                                     │
│   1. Implementar gestión automatizada de parches                   │
│      Responsable: María González, IT Manager                       │
│      Plazo: 60 días (2026-04-05)                                   │
│      Costo: $15,000                                                 │
│      Reducción esperada: 40% probabilidad                          │
│                                                                     │
│   2. Implementar backups offline inmutables                        │
│      Responsable: Carlos Rodríguez, Backup Admin                   │
│      Plazo: 30 días (2026-03-05)                                   │
│      Costo: $25,000                                                 │
│      Reducción esperada: 60% impacto                               │
│                                                                     │
│   3. Desplegar EDR en todos los servidores                         │
│      Responsable: Ana Martínez, Security Analyst                   │
│      Plazo: 45 días (2026-03-20)                                   │
│      Costo: $30,000/año                                             │
│      Reducción esperada: 50% probabilidad                          │
│                                                                     │
│ Riesgo Residual Objetivo:                                           │
│   Probabilidad: 1 (Muy Baja)                                       │
│   Impacto: 2 (Menor - recuperación en < 4 horas)                  │
│   Nivel: 2 (BAJO) 🟢                                               │
│                                                                     │
│ Inversión Total: $70,000 inicial + $30,000/año                     │
│ ROI: ALE reducido de $1M a $50K = ahorro $950K/año                │
├─────────────────────────────────────────────────────────────────────┤
│ SEGUIMIENTO                                                         │
├─────────────────────────────────────────────────────────────────────┤
│ Propietario del Riesgo: Laura Torres, VP de Operaciones            │
│ Frecuencia de Revisión: Mensual hasta implementación completa,     │
│                         trimestral después                         │
│ Próxima Revisión: 2026-03-05                                        │
│                                                                     │
│ KRIs (Key Risk Indicators):                                         │
│   - Días promedio para parchear vulnerabilidades críticas          │
│   - Éxito de restauración de backups (test mensual)                │
│   - Alertas de EDR críticas sin resolver > 24h                     │
├─────────────────────────────────────────────────────────────────────┤
│ HISTORIAL                                                           │
├─────────────────────────────────────────────────────────────────────┤
│ 2026-02-05: Riesgo identificado durante evaluación anual           │
│ 2026-02-05: Aprobado plan de tratamiento por CISO                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

**Documento**: risk-management-guide.md  
**Versión**: 1.0  
**Fecha**: Febrero 2026  
**Fuente**: ISO 27005:2022, NIST SP 800-30, FAIR Institute, ISACA Risk IT Framework  
**Idioma**: Español  
**Propósito**: Base de conocimiento para sistema RAG - CISO Digital con IA

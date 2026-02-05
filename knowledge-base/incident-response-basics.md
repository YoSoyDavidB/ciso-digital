# Fundamentos de Respuesta a Incidentes de Seguridad

## Resumen Ejecutivo

La respuesta a incidentes de seguridad es un proceso estructurado para detectar, analizar, contener, erradicar y recuperarse de incidentes de seguridad de la información, minimizando su impacto y previniendo futuros incidentes similares. Un programa efectivo de respuesta a incidentes reduce significativamente el tiempo de detección y recuperación, limita el daño financiero y reputacional, y cumple con requisitos regulatorios.

Esta guía proporciona fundamentos prácticos basados en frameworks reconocidos (NIST SP 800-61, SANS, ISO 27035) para establecer y operar una capacidad de respuesta a incidentes, desde la preparación inicial hasta las lecciones aprendidas post-incidente.

## ¿Qué es un Incidente de Seguridad?

Un **incidente de seguridad de la información** es cualquier evento que compromete la confidencialidad, integridad o disponibilidad de información o sistemas de información de una organización.

### Tipos Comunes de Incidentes

**1. Malware**
- Ransomware (cifrado de datos + rescate)
- Virus y gusanos
- Troyanos (RATs - Remote Access Trojans)
- Spyware y keyloggers
- Cryptominers maliciosos
- Wipers (destrucción de datos)

**2. Ataques de Phishing y Social Engineering**
- Phishing por email
- Spear phishing (dirigido)
- Whaling (dirigido a ejecutivos)
- Vishing (phishing por voz/teléfono)
- Smishing (phishing por SMS)
- Business Email Compromise (BEC)

**3. Accesos No Autorizados**
- Credential stuffing
- Brute force attacks
- Explotación de vulnerabilidades
- Escalación de privilegios
- Movimiento lateral no autorizado
- Insider threats (amenazas internas)

**4. Denegación de Servicio (DoS/DDoS)**
- Ataques volumétricos (saturación de ancho de banda)
- Ataques de protocolo (SYN flood, etc.)
- Ataques de aplicación (HTTP flood)
- Ataques distribuidos (DDoS)

**5. Exfiltración de Datos**
- Data breach (filtración de datos)
- Robo de propiedad intelectual
- Espionaje corporativo/estatal
- Pérdida de datos por insider

**6. Incidentes Web**
- Defacement (desfiguración de sitio web)
- SQL Injection
- Cross-Site Scripting (XSS)
- Inclusión de archivos remotos
- Secuestro de sesión

**7. Otros Incidentes**
- Pérdida o robo de dispositivos
- Configuraciones incorrectas expuestas
- Violaciones de políticas de seguridad
- Fallo de controles de seguridad
- Incidentes físicos (acceso no autorizado a instalaciones)

## Objetivos de Respuesta a Incidentes

1. **Detección Temprana**: Identificar incidentes lo más rápido posible
2. **Contención Rápida**: Limitar el alcance y prevenir propagación
3. **Minimizar Impacto**: Reducir daño financiero, operacional y reputacional
4. **Recuperación Efectiva**: Restaurar operaciones normales
5. **Preservar Evidencia**: Para análisis forense e investigaciones legales
6. **Aprender y Mejorar**: Prevenir incidentes similares en el futuro
7. **Cumplimiento**: Satisfacer requisitos regulatorios de notificación y respuesta

## Ciclo de Vida de Respuesta a Incidentes

### Framework NIST (6 Fases)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. PREPARACIÓN                                             │
│  ├─ Establecer capacidades y recursos                      │
│  ├─ Capacitar al equipo                                    │
│  └─ Desarrollar playbooks y procedimientos                 │
│                                                             │
│  ↓                                                          │
│                                                             │
│  2. DETECCIÓN Y ANÁLISIS                                    │
│  ├─ Monitorear eventos de seguridad                        │
│  ├─ Identificar indicadores de compromiso (IoCs)           │
│  ├─ Determinar alcance y severidad                         │
│  └─ Priorizar incidentes                                   │
│                                                             │
│  ↓                                                          │
│                                                             │
│  3. CONTENCIÓN                                              │
│  ├─ Contención a corto plazo (aislar sistema)              │
│  ├─ Contención a largo plazo (reconstruir sistemas)        │
│  └─ Preservar evidencia                                    │
│                                                             │
│  ↓                                                          │
│                                                             │
│  4. ERRADICACIÓN                                            │
│  ├─ Eliminar artefactos maliciosos                         │
│  ├─ Cerrar vectores de acceso                              │
│  └─ Remediar vulnerabilidades explotadas                   │
│                                                             │
│  ↓                                                          │
│                                                             │
│  5. RECUPERACIÓN                                            │
│  ├─ Restaurar sistemas desde backups limpios               │
│  ├─ Validar operación normal                               │
│  ├─ Monitoreo intensivo post-recuperación                  │
│  └─ Retorno a operaciones normales                         │
│                                                             │
│  ↓                                                          │
│                                                             │
│  6. LECCIONES APRENDIDAS (Post-Incident Activity)          │
│  ├─ Reunión post-mortem                                    │
│  ├─ Documentar timeline y acciones                         │
│  ├─ Identificar mejoras                                    │
│  └─ Actualizar playbooks y controles                       │
│                                                             │
│  ↓ (Ciclo continuo - volver a Preparación)                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Fase 1: Preparación

**Objetivo**: Establecer capacidad para responder efectivamente a incidentes antes de que ocurran.

### Componentes Clave

#### 1. Equipo de Respuesta a Incidentes (CSIRT/CERT)

**Roles y Responsabilidades**:

```
┌─────────────────────────────────────────────────────────────┐
│ INCIDENT RESPONSE TEAM                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ CISO / IR Manager                                           │
│ ├─ Liderazgo general del programa                          │
│ ├─ Comunicación con ejecutivos                             │
│ ├─ Decisiones de escalamiento                              │
│ └─ Aprobación de comunicaciones externas                   │
│                                                             │
│ Incident Commander (Líder de Incidente)                     │
│ ├─ Coordinar respuesta durante incidente activo            │
│ ├─ Tomar decisiones tácticas                               │
│ ├─ Gestionar comunicaciones internas                       │
│ └─ Documentar timeline y acciones                          │
│                                                             │
│ Security Analysts (Analistas de Seguridad)                  │
│ ├─ Monitoreo de SIEM y alertas                             │
│ ├─ Análisis inicial de alertas                             │
│ ├─ Triaje de incidentes                                    │
│ └─ Documentación de hallazgos                              │
│                                                             │
│ Forensics Specialist (Especialista Forense)                 │
│ ├─ Recolección de evidencia                                │
│ ├─ Análisis forense de sistemas/memoria/red                │
│ ├─ Reconstrucción de timeline                              │
│ └─ Cadena de custodia                                      │
│                                                             │
│ Threat Intelligence Analyst                                 │
│ ├─ Investigación de IoCs                                   │
│ ├─ Análisis de TTPs del atacante                           │
│ ├─ Contexto de amenazas                                    │
│ └─ Threat hunting proactivo                                │
│                                                             │
│ IT/Systems Administrator                                    │
│ ├─ Implementar medidas de contención                       │
│ ├─ Aplicar parches y remediaciones                         │
│ ├─ Recuperación de sistemas                                │
│ └─ Coordinación con equipos técnicos                       │
│                                                             │
│ Legal Counsel (Asesor Legal)                                │
│ ├─ Evaluación de obligaciones legales                      │
│ ├─ Requisitos de notificación                              │
│ ├─ Interacción con fuerzas del orden                       │
│ └─ Protección de evidencia para litigios                   │
│                                                             │
│ Communications/PR (Comunicaciones)                          │
│ ├─ Comunicación con clientes/socios                        │
│ ├─ Declaraciones públicas                                  │
│ ├─ Gestión de crisis de reputación                         │
│ └─ Coordinación con medios                                 │
│                                                             │
│ Business Representatives (Representantes de Negocio)        │
│ ├─ Evaluación de impacto en negocio                        │
│ ├─ Decisiones de continuidad                               │
│ ├─ Priorización de sistemas para recuperación              │
│ └─ Comunicación con usuarios afectados                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Modelos de Equipo**:

- **In-house 24/7 SOC**: Ideal pero costoso ($500K-$2M/año)
- **Business hours + on-call**: Común en medianas empresas
- **Outsourced SOC/MDR**: $50K-$200K/año, cobertura 24/7
- **Híbrido**: SOC externo + especialistas internos

#### 2. Herramientas y Tecnología

**Stack Mínimo de Herramientas**:

```
DETECCIÓN Y MONITOREO:
├─ SIEM (Security Information and Event Management)
│  ├─ Splunk Enterprise Security ($5K-$50K/año)
│  ├─ Elastic Security (Open source / Enterprise)
│  ├─ Microsoft Sentinel ($2-$5/GB ingestion)
│  └─ IBM QRadar, LogRhythm, etc.
│
├─ EDR/XDR (Endpoint Detection and Response)
│  ├─ CrowdStrike Falcon (~$8-$15/endpoint/mes)
│  ├─ Microsoft Defender for Endpoint (~$5/user/mes)
│  ├─ SentinelOne (~$6-$10/endpoint/mes)
│  └─ Carbon Black, Cortex XDR, etc.
│
├─ NDR (Network Detection and Response)
│  ├─ Zeek (open source)
│  ├─ Suricata (open source IDS/IPS)
│  ├─ Darktrace (~$50K-$200K/año)
│  └─ ExtraHop, Vectra AI
│
└─ Threat Intelligence Platform
   ├─ MISP (open source)
   ├─ ThreatConnect
   ├─ Anomali ThreatStream
   └─ Feeds: CISA KEV, AlienVault OTX, etc.

RESPUESTA Y ANÁLISIS:
├─ SOAR (Security Orchestration, Automation, Response)
│  ├─ Palo Alto Cortex XSOAR
│  ├─ Splunk SOAR (Phantom)
│  ├─ IBM Resilient
│  └─ TheHive (open source)
│
├─ Case Management
│  ├─ JIRA + plugins
│  ├─ ServiceNow Security IR
│  ├─ TheHive
│  └─ Remedy, etc.
│
├─ Forensics Tools
│  ├─ Volatility (memory forensics, open source)
│  ├─ Autopsy (disk forensics, open source)
│  ├─ FTK Imager (disk imaging, free)
│  ├─ Wireshark (network analysis, open source)
│  ├─ EnCase, X-Ways (comerciales)
│  └─ Velociraptor (endpoint forensics, open source)
│
└─ Malware Analysis
   ├─ ANY.RUN (sandbox comercial)
   ├─ Hybrid Analysis (gratuito)
   ├─ VirusTotal (gratuito/comercial)
   ├─ Cuckoo Sandbox (open source)
   └─ REMnux (distro Linux para malware RE)

COMUNICACIÓN:
├─ Secure Communication
│  ├─ Signal (mensajería encriptada)
│  ├─ Wickr
│  └─ Secure email (PGP/S/MIME)
│
└─ Collaboration
   ├─ Slack / Microsoft Teams (canales privados)
   ├─ War room físico/virtual
   └─ Shared documentation (Confluence, SharePoint)
```

#### 3. Playbooks de Respuesta

**Estructura de un Playbook**:

```markdown
# PLAYBOOK: Ransomware Response

## Metadata
- **ID**: PB-001
- **Versión**: 2.1
- **Última Actualización**: 2026-01-15
- **Propietario**: Juan Pérez, CISO
- **Severidad Típica**: Crítica / Alta

## Descripción
Este playbook guía la respuesta a incidentes de ransomware, desde 
detección inicial hasta recuperación completa.

## Indicadores de Ransomware
- Archivos encriptados con extensiones inusuales (.locked, .encrypted, etc.)
- Notas de rescate (ransom notes) en directorios
- Alertas de EDR: ejecución de herramientas de cifrado
- Actividad inusual de red (C2 communication)
- Desactivación de backups o shadow copies
- Escalación de privilegios sospechosa

## Fase 1: DETECCIÓN Y TRIAJE (15 minutos)
### Acciones Inmediatas:
1. [ ] Documentar hora de detección y fuente del alerta
2. [ ] Identificar sistema(s) afectado(s) inicialmente
3. [ ] Verificar si es ransomware real o falso positivo
4. [ ] Determinar variante de ransomware si es posible (ID Ransomware)
5. [ ] Evaluar alcance inicial (¿cuántos sistemas?)
6. [ ] Notificar a Incident Commander

### Criterios de Escalamiento:
- ☐ Más de 5 sistemas afectados → Escalar a Nivel 2
- ☐ Sistemas críticos de negocio → Escalar inmediatamente
- ☐ Controladores de dominio afectados → Escalar inmediatamente
- ☐ Evidencia de exfiltración de datos → Involucrar Legal

## Fase 2: CONTENCIÓN (30-60 minutos)
### Contención de Red:
1. [ ] Aislar sistema(s) afectado(s) de la red (no apagar aún)
   - Desconectar de switch o deshabilitar puerto
   - Reglas de firewall para bloquear tráfico
   - VLAN de cuarentena si está disponible

2. [ ] Identificar otros sistemas potencialmente comprometidos
   - Buscar IoCs en SIEM/EDR (hashes, IPs C2, etc.)
   - Revisar movimiento lateral desde sistema inicial
   - Identificar cuentas comprometidas

3. [ ] Bloquear propagación:
   - Deshabilitar cuentas comprometidas
   - Bloquear IPs/dominios C2 en firewall
   - Deshabilitar servicios de compartición de archivos (SMB)
   - Desconectar backups online de la red

4. [ ] Proteger sistemas críticos:
   - Aislar controladores de dominio
   - Proteger servidores de backup
   - Segregar sistemas de producción críticos

### Preservación de Evidencia:
1. [ ] Crear imagen de memoria RAM (antes de apagar)
   - Usar FTK Imager, Magnet RAM Capture, o similar
2. [ ] Capturar procesos en ejecución
3. [ ] Documentar conexiones de red activas
4. [ ] Tomar screenshots de notas de rescate
5. [ ] Preservar logs relevantes

### Decisión: ¿Apagar sistemas infectados?
- **NO APAGAR** si:
  - Análisis forense en vivo es necesario
  - Evidencia volátil no ha sido capturada
  - Sistema contiene datos críticos no respaldados
- **APAGAR** si:
  - Cifrado está en progreso activamente
  - No hay capacidad de análisis inmediato
  - Riesgo de propagación es muy alto

## Fase 3: ERRADICACIÓN Y ANÁLISIS (2-4 horas)
### Análisis de Malware:
1. [ ] Identificar variante de ransomware
   - ID Ransomware (id-ransomware.malwarehunterteam.com)
   - No More Ransom (nomoreransom.org)
   - Análisis en sandbox (ANY.RUN, Hybrid Analysis)

2. [ ] Identificar IoCs:
   - Hashes de archivos maliciosos
   - URLs/IPs de C2
   - Persistencia (registry, scheduled tasks)
   - Herramientas utilizadas (PSExec, Mimikatz, etc.)

3. [ ] Determinar vector de infección inicial:
   - Phishing email
   - RDP expuesto
   - Vulnerabilidad explotada
   - Credenciales comprometidas

4. [ ] Evaluar si hubo exfiltración de datos:
   - Revisar tráfico de red saliente
   - Buscar herramientas de exfiltración (rclone, MEGAsync)
   - Analizar si es doble extorsión

### Erradicación:
1. [ ] Eliminar persistencia del malware
2. [ ] Remover artefactos maliciosos
3. [ ] Cerrar vector de infección inicial
4. [ ] Cambiar todas las credenciales potencialmente comprometidas
5. [ ] Aplicar parches para vulnerabilidades explotadas

## Fase 4: RECUPERACIÓN (variable: horas a días)
### Evaluación de Opciones:
1. [ ] ¿Existe descifrador disponible?
   - Buscar en No More Ransom
   - Buscar en vendors de seguridad
   
2. [ ] ¿Backups están disponibles y limpios?
   - Verificar integridad de backups
   - Confirmar que backups no están comprometidos
   - Identificar último backup limpio (puede ser pre-infección)

3. [ ] ¿Pagar rescate? (última opción)
   - Evaluación legal y ética
   - No hay garantía de recuperación
   - Financia actividad criminal
   - Considerar solo si: datos críticos + sin backups + negocio en riesgo inminente

### Recuperación desde Backups (opción preferida):
1. [ ] Validar que amenaza está erradicada completamente
2. [ ] Reconstruir sistemas desde cero (no restaurar sobre infectado)
3. [ ] Restaurar datos desde backup limpio
4. [ ] Aplicar hardenings y controles adicionales
5. [ ] Cambiar todas las credenciales
6. [ ] Monitoreo intensivo por 30 días

### Timeline de Recuperación:
- Sistemas Críticos (Tier 1): 4-8 horas
- Sistemas Importantes (Tier 2): 8-24 horas
- Sistemas Normales (Tier 3): 24-72 horas

## Fase 5: COMUNICACIÓN
### Comunicaciones Internas:
- [ ] Actualizar a alta dirección cada 4 horas
- [ ] Notificar a equipos afectados
- [ ] Coordinar con RR.HH. para comunicación a empleados
- [ ] Actualizar status en portal interno

### Comunicaciones Externas (si aplicable):
- [ ] Notificar a autoridades regulatorias (GDPR: 72 horas)
- [ ] Notificar a clientes afectados
- [ ] Reportar a fuerzas del orden (FBI IC3, etc.)
- [ ] Notificar a aseguradora cibernética
- [ ] Coordinar declaraciones públicas con PR

## Fase 6: POST-INCIDENTE
### Reunión de Lecciones Aprendidas (1-2 semanas después):
- [ ] Documentar timeline completo
- [ ] Analizar qué funcionó y qué no
- [ ] Identificar mejoras en:
  - Detección (¿por qué no detectamos antes?)
  - Respuesta (¿qué retrasó la contención?)
  - Recuperación (¿problemas con backups?)
  - Comunicación (¿fue efectiva?)

### Mejoras a Implementar:
- [ ] Actualizar playbook basado en experiencia
- [ ] Implementar controles adicionales
- [ ] Capacitación adicional si es necesaria
- [ ] Actualizar evaluación de riesgos

## Contactos Clave
- **Incident Commander**: Juan Pérez, +34 600-000-001
- **CISO**: María González, +34 600-000-002
- **IT Manager**: Carlos Rodríguez, +34 600-000-003
- **Legal**: Laura Torres, +34 600-000-004
- **PR/Comunicaciones**: Ana Martínez, +34 600-000-005
- **Vendor EDR Support**: CrowdStrike: 1-888-512-8906
- **Vendor Backup Support**: Veeam: +1-614-339-8200
- **FBI Cyber**: 1-800-CALL-FBI, ic3.gov

## Referencias
- NIST SP 800-61r2: Computer Security Incident Handling Guide
- CISA Ransomware Guide: cisa.gov/ransomware
- No More Ransom: nomoreransom.org
- ID Ransomware: id-ransomware.malwarehunterteam.com

---
**Última Prueba (Tabletop Exercise)**: 2025-11-15
**Próxima Revisión Programada**: 2026-05-01
```

**Playbooks Esenciales**:
1. Ransomware Response ⬆️
2. Phishing / Business Email Compromise
3. Data Breach / Exfiltration
4. DDoS Attack
5. Web Application Compromise
6. Insider Threat
7. Malware Outbreak
8. Unauthorized Access
9. Lost/Stolen Device
10. Supply Chain Compromise

#### 4. Capacitación y Ejercicios

**Programas de Capacitación**:

- **Capacitación Inicial** (40 horas):
  - Fundamentos de respuesta a incidentes
  - Uso de herramientas (SIEM, EDR, forensics)
  - Playbooks y procedimientos
  - Comunicación de crisis

- **Capacitación Continua** (trimestral):
  - Nuevas amenazas y TTPs
  - Actualizaciones de herramientas
  - Lecciones aprendidas de incidentes reales
  - Capacitación en nuevos playbooks

**Ejercicios y Simulaciones**:

1. **Tabletop Exercises** (trimestral):
   - Discusión de escenario hipotético
   - Evaluar procedimientos y comunicación
   - Identificar gaps
   - Duración: 2-4 horas
   - Costo: Bajo (interno)

2. **Simulaciones Técnicas** (semestral):
   - Inyección de alertas simuladas en SIEM
   - Equipo responde como si fuera real
   - Evaluar detección y respuesta técnica
   - Duración: 4-8 horas

3. **Red Team / Purple Team** (anual):
   - Simulación de ataque real por red team
   - Blue team defiende
   - Purple team facilita aprendizaje
   - Duración: 1-2 semanas
   - Costo: $20K-$100K (si se contrata externo)

---

## Fase 2: Detección y Análisis

**Objetivo**: Identificar y analizar incidentes de seguridad rápidamente y con precisión.

### Fuentes de Detección

1. **SIEM (Security Information and Event Management)**
   - Correlación de eventos de múltiples fuentes
   - Alertas basadas en reglas y anomalías
   - Casos de uso: failed logins, privilege escalation, data exfiltration

2. **EDR/XDR (Endpoint/Extended Detection and Response)**
   - Comportamiento anómalo de procesos
   - Ejecución de malware conocido/desconocido
   - Movimiento lateral
   - Técnicas de ataque (MITRE ATT&CK)

3. **IDS/IPS (Intrusion Detection/Prevention System)**
   - Tráfico de red malicioso
   - Exploits conocidos
   - Comunicación con C2

4. **Threat Intelligence**
   - IoCs conocidos (IPs, dominios, hashes maliciosos)
   - Campañas de amenazas activas
   - Vulnerabilidades siendo explotadas (KEV)

5. **Reportes de Usuarios**
   - Emails sospechosos
   - Comportamiento anómalo de sistemas
   - Accesos no autorizados

6. **Escaneos de Vulnerabilidades**
   - Vulnerabilidades críticas sin parchear
   - Configuraciones inseguras

### Proceso de Triaje

**Nivel 1 - Screening Inicial** (5-10 minutos):
```
1. ¿Es un falso positivo?
   └─ Sí → Cerrar, ajustar regla de detección
   └─ No → Continuar

2. ¿Es realmente un incidente de seguridad?
   └─ No → Categorizar como evento, no incidente
   └─ Sí → Continuar

3. Clasificar tipo de incidente
   └─ Malware, Phishing, Acceso no autorizado, DDoS, etc.

4. Asignar severidad inicial
   └─ Crítico, Alto, Medio, Bajo

5. Asignar a analista Nivel 2 o escalar según severidad
```

**Criterios de Severidad**:

```
CRÍTICO (P1):
├─ Sistema crítico de negocio comprometido
├─ Múltiples sistemas afectados y propagándose
├─ Controladores de dominio comprometidos
├─ Ransomware activo
├─ Exfiltración de datos confirmada
└─ SLA: Respuesta inmediata (< 15 minutos)

ALTO (P2):
├─ Sistema importante comprometido
├─ Evidencia de movimiento lateral
├─ Credenciales privilegiadas comprometidas
├─ Malware no contenido
└─ SLA: Respuesta en 1 hora

MEDIO (P3):
├─ Sistema no crítico comprometido
├─ Malware contenido
├─ Intento de acceso no autorizado (bloqueado)
├─ Phishing dirigido a empleados
└─ SLA: Respuesta en 4 horas

BAJO (P4):
├─ Evento de seguridad sin compromiso confirmado
├─ Escaneos de red desde internet
├─ Phishing genérico (bloqueado)
└─ SLA: Respuesta en 24 horas
```

### Análisis de Incidentes

**Preguntas Clave**:
1. **¿Qué ocurrió?** - Naturaleza del incidente
2. **¿Cuándo ocurrió?** - Timeline (inicio, detección, contención)
3. **¿Dónde ocurrió?** - Sistemas/redes afectados
4. **¿Cómo ocurrió?** - Vector de ataque, TTPs
5. **¿Quién está afectado?** - Usuarios, clientes, datos
6. **¿Por qué ocurrió?** - Causa raíz (vulnerabilidad, configuración, etc.)
7. **¿Cuál es el impacto?** - Financiero, operacional, reputacional

**Técnicas de Análisis**:

1. **Log Analysis**: Revisar logs de sistemas afectados (Windows Event Logs, Syslog, application logs)
2. **Network Traffic Analysis**: Capturar y analizar tráfico (Wireshark, Zeek)
3. **Memory Forensics**: Analizar memoria RAM (Volatility)
4. **Disk Forensics**: Analizar discos (Autopsy, FTK)
5. **Malware Analysis**: Analizar binarios maliciosos (sandboxes, reverse engineering)
6. **Threat Intelligence**: Correlacionar IoCs con threat feeds

---

## Fase 3: Contención

**Objetivo**: Limitar el alcance del incidente y prevenir daño adicional.

### Estrategias de Contención

**Contención a Corto Plazo** (minutos a horas):
- Aislar sistemas afectados de la red
- Bloquear IPs/dominios maliciosos
- Deshabilitar cuentas comprometidas
- Apagar sistemas si es necesario (último recurso)

**Contención a Largo Plazo** (horas a días):
- Aplicar parches de emergencia
- Implementar controles compensatorios
- Segmentar red para limitar movimiento lateral
- Reconstruir sistemas comprometidos

### Consideraciones de Contención

**Balance entre Contención y Operaciones**:
- ¿Apagar sistema crítico de negocio? → Evaluar impacto de negocio vs. riesgo de seguridad
- ¿Cerrar acceso remoto completamente? → Considerar necesidades de negocio

**Preservación de Evidencia**:
- Contener SIN destruir evidencia forense
- Documentar todas las acciones tomadas
- Mantener cadena de custodia

---

## Fase 4: Erradicación

**Objetivo**: Eliminar la causa raíz del incidente.

### Actividades de Erradicación

1. **Eliminar Malware**:
   - Remover binarios maliciosos
   - Eliminar persistencia (registry, scheduled tasks, services)
   - Limpiar archivos temporales

2. **Cerrar Vulnerabilidades**:
   - Aplicar parches
   - Corregir configuraciones inseguras
   - Implementar controles adicionales

3. **Revocar Accesos Comprometidos**:
   - Cambiar contraseñas de cuentas afectadas
   - Rotar credenciales de servicio
   - Invalidar sesiones activas

4. **Verificar Erradicación**:
   - Escanear sistemas con antimalware actualizado
   - Buscar IoCs conocidos
   - Monitorear para reinfección

---

## Fase 5: Recuperación

**Objetivo**: Restaurar sistemas a operación normal y monitorear para recurrencia.

### Proceso de Recuperación

1. **Restaurar desde Backups** (opción preferida):
   - Validar que backups están limpios
   - Restaurar datos
   - Verificar integridad

2. **Reconstruir Sistemas** (para sistemas comprometidos):
   - Reinstalar OS desde medios limpios
   - Aplicar hardenings de seguridad
   - Reinstalar aplicaciones
   - Restaurar datos desde backup limpio

3. **Validación**:
   - Verificar funcionalidad de sistemas
   - Confirmar que no hay malware residual
   - Probar conectividad y servicios

4. **Retorno a Producción**:
   - Monitoreo intensivo inicial (24-48 horas)
   - Retorno gradual a operaciones normales
   - Comunicar a usuarios

### Monitoreo Post-Recuperación

**Período Intensivo** (primeras 2-4 semanas):
- Monitoreo continuo de IoCs relacionados
- Alertas elevadas para sistemas recuperados
- Revisiones diarias de logs
- Reuniones de status frecuentes

---

## Fase 6: Lecciones Aprendidas

**Objetivo**: Mejorar capacidades de respuesta para futuros incidentes.

### Reunión Post-Mortem

**Timing**: 1-2 semanas después de incidente cerrado

**Participantes**:
- Equipo de respuesta completo
- Propietarios de sistemas afectados
- Representantes de negocio
- Dirección (CISO, CIO)

**Agenda**:
1. **Timeline de Incidente** (30 min)
   - ¿Cuándo comenzó realmente el incidente?
   - ¿Cuándo lo detectamos?
   - ¿Cuánto duró hasta contención?
   - ¿Cuánto hasta recuperación completa?

2. **¿Qué Funcionó Bien?** (20 min)
   - Detección efectiva
   - Respuesta rápida
   - Herramientas efectivas
   - Comunicación clara

3. **¿Qué No Funcionó?** (30 min)
   - Gaps en detección
   - Retrasos en respuesta
   - Herramientas faltantes o inefectivas
   - Problemas de comunicación
   - Documentación inadecuada

4. **Causa Raíz** (20 min)
   - ¿Por qué ocurrió el incidente?
   - ¿Qué vulnerabilidad/debilidad se explotó?
   - ¿Por qué no lo prevenimos?

5. **Mejoras a Implementar** (30 min)
   - Controles preventivos adicionales
   - Mejoras en detección
   - Actualizaciones de playbooks
   - Capacitación necesaria
   - Inversiones requeridas

### Documentación Post-Incidente

**Informe de Incidente** debe incluir:

```markdown
# Incident Report - [Incident ID]

## Executive Summary
[Resumen de 1 página para ejecutivos]

## Incident Details
- **ID**: INC-2026-001
- **Fecha de Inicio**: 2026-02-01 03:45 UTC
- **Fecha de Detección**: 2026-02-01 08:30 UTC
- **Fecha de Contención**: 2026-02-01 11:00 UTC
- **Fecha de Recuperación**: 2026-02-02 14:00 UTC
- **Severidad**: Crítica
- **Tipo**: Ransomware
- **Sistemas Afectados**: 15 servidores, 45 workstations

## Timeline
[Timeline detallado con timestamps]

## Technical Analysis
- Vector de infección
- TTPs del atacante (MITRE ATT&CK mapping)
- IoCs identificados
- Alcance del compromiso

## Impact Assessment
- Impacto financiero: $XXX
- Tiempo de inactividad: XX horas
- Datos afectados: XXX registros
- Clientes impactados: XXX

## Response Actions
- Contención
- Erradicación
- Recuperación
- Comunicaciones

## Root Cause
[Análisis de causa raíz]

## Lessons Learned
- Lo que funcionó
- Lo que no funcionó
- Mejoras identificadas

## Action Items
1. [Acción] - Responsable: [Persona] - Fecha: [Deadline]
2. [...]

## Appendices
- A: IoCs completos
- B: Logs relevantes
- C: Screenshots
- D: Comunicaciones externas
```

---

## Métricas de Respuesta a Incidentes

### KPIs (Key Performance Indicators)

**Métricas de Detección**:
```
MTTD (Mean Time To Detect): Tiempo promedio desde inicio de incidente hasta detección
└─ Objetivo: < 24 horas (idealmente < 1 hora)

False Positive Rate: % de alertas que son falsos positivos
└─ Objetivo: < 30%

Coverage: % de activos con monitoreo de seguridad
└─ Objetivo: 100% de activos críticos, > 95% de todos los activos
```

**Métricas de Respuesta**:
```
MTTR (Mean Time To Respond): Tiempo desde detección hasta inicio de respuesta
└─ Objetivo: < 1 hora para incidentes críticos

MTTC (Mean Time To Contain): Tiempo desde detección hasta contención
└─ Objetivo: < 4 horas para incidentes críticos

MTTR (Mean Time To Recover): Tiempo desde detección hasta recuperación completa
└─ Objetivo: < 24 horas para incidentes críticos (depende de tipo)
```

**Métricas de Efectividad**:
```
Incident Recurrence Rate: % de incidentes que recurren
└─ Objetivo: < 5%

Escalation Rate: % de incidentes que requieren escalamiento
└─ Objetivo: < 20%

Post-Incident Action Completion: % de acciones de mejora completadas
└─ Objetivo: > 90% en 90 días
```

---

## Comunicación Durante Incidentes

### Comunicación Interna

**Niveles de Comunicación**:

1. **Executive Leadership** (CEO, Board):
   - Frecuencia: Inicio + cada 4-6 horas para críticos
   - Formato: Brief verbal + email resumen
   - Contenido: Impacto de negocio, timeline, próximos pasos

2. **Management** (VPs, Directors):
   - Frecuencia: Cada 2-4 horas
   - Formato: Email updates, calls de status
   - Contenido: Status técnico, impacto a operaciones

3. **Equipo de Respuesta**:
   - Frecuencia: Continua
   - Formato: Slack/Teams, war room calls
   - Contenido: Detalles técnicos, tareas, hallazgos

4. **Usuarios Afectados**:
   - Frecuencia: Según necesidad
   - Formato: Email, intranet, Teams
   - Contenido: Impacto a sus sistemas, workarounds, ETAs

### Comunicación Externa

**Obligaciones Legales de Notificación**:

```
GDPR (Unión Europea):
├─ Timeline: 72 horas desde conocimiento de la brecha
├─ Destinatario: Autoridad de protección de datos (DPA)
├─ Contenido: Naturaleza, datos afectados, consecuencias, medidas tomadas
└─ Penalización por no notificar: Hasta €20M o 4% de revenue global

CCPA (California):
├─ Timeline: Sin tiempo específico ("sin demora irrazonable")
├─ Destinatario: Residentes de California afectados
├─ Umbral: > 500 residentes → también notificar a Attorney General
└─ Penalización: $100-$750 por consumidor por incidente

HIPAA (US Healthcare):
├─ Timeline: 60 días
├─ Destinatario: HHS, individuos afectados, medios (si > 500 personas)
└─ Penalización: $100-$50,000 por registro, máx $1.5M/año

PCI-DSS (Payment Cards):
├─ Timeline: Inmediato (typical 24 horas)
├─ Destinatario: Acquiring bank, card brands
└─ Consecuencia: Multas, pérdida de capacidad de procesar tarjetas
```

**Plantilla de Notificación**:
```
Subject: [URGENT] Security Incident Notification - [Company Name]

Dear [Customer/Partner],

We are writing to inform you of a security incident that may have 
affected your personal information.

WHAT HAPPENED:
On [date], we discovered [type of incident]. We immediately initiated 
our incident response procedures and [actions taken].

WHAT INFORMATION WAS INVOLVED:
The incident may have involved the following types of information:
[list of data types - names, emails, SSN, etc.]

WHAT WE ARE DOING:
- [Containment actions]
- [Investigation actions]
- [Prevention actions]
- [Offering credit monitoring if applicable]

WHAT YOU CAN DO:
- [Recommendations for affected individuals]
- [Resources provided]
- [Contact information]

FOR MORE INFORMATION:
[Contact email, phone, dedicated website]

We sincerely apologize for this incident and any concern it may cause.

Sincerely,
[Name, Title]
[Company]
```

---

## Mejores Prácticas

### 1. Prepararse Antes de que Ocurra
- Tener playbooks actualizados
- Capacitar regularmente
- Hacer ejercicios (tabletop, simulaciones)
- Mantener herramientas actualizadas

### 2. Documentar TODO
- Timeline preciso
- Acciones tomadas
- Decisiones y justificaciones
- Evidencia preservada

### 3. Comunicar Clara y Frecuentemente
- Mantener a stakeholders informados
- Usar terminología apropiada a la audiencia
- No especular, reportar hechos

### 4. Preservar Evidencia
- Mantener cadena de custodia
- No contaminar evidencia
- Documentar recolección

### 5. Aprender de Cada Incidente
- Post-mortem obligatorio
- Implementar mejoras identificadas
- Actualizar playbooks
- Compartir lecciones (si apropiado)

### 6. No Reinventar la Rueda
- Usar frameworks establecidos (NIST, SANS)
- Aprovechar recursos comunitarios
- Colaborar con peers e ISACs

### 7. Automatizar Donde Sea Posible
- SOAR para acciones repetitivas
- Playbooks automatizados
- Enrichment automático de IoCs

### 8. Practicar Gestión del Estrés
- Incidentes son estresantes
- Turnos para evitar burnout
- Apoyo psicológico si es necesario

---

## Recursos y Referencias

### Frameworks y Guías
- **NIST SP 800-61r2**: Computer Security Incident Handling Guide
- **NIST SP 800-83**: Guide to Malware Incident Prevention and Handling
- **ISO/IEC 27035**: Information security incident management
- **SANS Incident Handler's Handbook**: sansorg
- **CISA Incident Response Resources**: cisa.gov/incident-response

### Herramientas y Utilidades
- **TheHive Project**: thehive-project.org (case management, open source)
- **MISP**: misp-project.org (threat intel sharing, open source)
- **MITRE ATT&CK**: attack.mitre.org (adversary TTPs)
- **Incident Response Consortium**: incidentresponse.com (playbooks)

### Comunidades y Colaboración
- **US-CERT**: us-cert.gov
- **FIRST**: first.org (Forum of Incident Response and Security Teams)
- **ISACs**: Sector-specific information sharing (FS-ISAC, H-ISAC, etc.)

---

**Documento**: incident-response-basics.md  
**Versión**: 1.0  
**Fecha**: Febrero 2026  
**Fuente**: NIST SP 800-61r2, SANS, ISO 27035, CISA  
**Idioma**: Español  
**Propósito**: Base de conocimiento para sistema RAG - CISO Digital con IA

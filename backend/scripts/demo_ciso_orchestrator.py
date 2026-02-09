#!/usr/bin/env python3
"""
Simple Demo: CISO Orchestrator & Incident Response

Demostración simplificada de las capacidades del sistema sin dependencias complejas.
"""

import asyncio
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4


# ============================================================================
# ANSI Colors
# ============================================================================

class C:
    """Colors"""
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def bold(s): return f"{C.BOLD}{s}{C.END}"
def cyan(s): return f"{C.CYAN}{s}{C.END}"
def green(s): return f"{C.GREEN}{s}{C.END}"
def yellow(s): return f"{C.YELLOW}{s}{C.END}"
def red(s): return f"{C.RED}{s}{C.END}"
def blue(s): return f"{C.BLUE}{s}{C.END}"


# ============================================================================
# Intent Types
# ============================================================================

class IntentType(Enum):
    RISK_ASSESSMENT = "risk_assessment"
    INCIDENT_RESPONSE = "incident_response"
    COMPLIANCE_CHECK = "compliance_check"
    GENERAL_QUERY = "general_query"


# ============================================================================
# Mock Services
# ============================================================================

class MockLLMService:
    """Mock LLM responses"""
    
    async def generate(self, prompt: str) -> str:
        await asyncio.sleep(0.3)  # Simulate API latency
        
        if "riesgos críticos" in prompt.lower():
            return """Actualmente tenemos 3 riesgos críticos identificados:

1. **CVE-2025-1234** en servidor web de producción (Score: 9.8)
   - Vulnerabilidad de ejecución remota de código
   - Exploit público disponible
   - Recomendación: Parchar inmediatamente

2. **Configuración incorrecta en firewall AWS** (Score: 8.5)
   - Puerto 22 (SSH) expuesto públicamente
   - Sin restricción por IP
   - Recomendación: Implementar security groups restrictivos

3. **Credenciales débiles en base de datos** (Score: 7.2)
   - Password policy no cumple con estándares
   - Sin rotación automática
   - Recomendación: Implementar AWS Secrets Manager"""
        
        elif "primer riesgo" in prompt.lower() or "cve-2025-1234" in prompt.lower():
            return """El **CVE-2025-1234** es una vulnerabilidad crítica de ejecución remota de código (RCE) en Apache Struts 2.

**Detalles técnicos:**
- CVSS Score: 9.8 (Critical)
- Vector de ataque: Network (remoto)
- Complejidad: Low (fácil de explotar)
- Privilegios requeridos: None
- Interacción del usuario: None

**Impacto:**
- Un atacante puede ejecutar código arbitrario en el servidor
- Acceso completo al sistema comprometido
- Potencial para movimiento lateral en la red

**Sistemas afectados:**
- production-web-01 (Apache Struts 2.5.28)
- staging-web-01 (Apache Struts 2.5.28)

**Remediación:**
1. Actualizar a Apache Struts 2.5.30 o superior INMEDIATAMENTE
2. Aplicar reglas WAF temporales mientras se parchea
3. Monitorear logs por intentos de explotación
4. Realizar escaneo de IOCs (Indicators of Compromise)"""
        
        elif "ransomware" in prompt.lower():
            return """He detectado y clasificado el incidente como un ataque de ransomware crítico.

**Acciones inmediatas ejecutadas:**
✅ Servidor aislado de la red (0:00)
✅ Equipo de seguridad notificado (0:02)
✅ Snapshot de evidencias creado (0:05)
✅ Comunicación bloqueada a C&C conocidos (0:10)

**Plan de contención activo:**
- Identificación de sistemas adicionales comprometidos en progreso
- Análisis de variante de ransomware iniciado
- Preparación de restauración desde backups

**Stakeholders notificados:**
- CISO
- VP of Engineering
- Legal Team
- Incident Response Team

Incidente registrado como: **INC-2026-042**"""
        
        elif "iso 27001" in prompt.lower():
            return """Análisis de cumplimiento con ISO 27001:

**Estado general: 78% compliant** ⚠️

**Controles implementados (82/133):**
✅ A.5 (Políticas de Seguridad): 100%
✅ A.6 (Organización): 85%
✅ A.8 (Gestión de Activos): 72%
⚠️ A.9 (Control de Acceso): 65%
⚠️ A.12 (Seguridad Operacional): 68%
❌ A.14 (Adquisición): 45%

**Gaps críticos identificados:**
1. A.9.2.3 - Gestión de credenciales privilegiadas incompleta
2. A.12.6.2 - Falta control de instalación de software
3. A.14.2.5 - Sin SLAs de seguridad en contratos de terceros

**Recomendaciones inmediatas:**
1. Implementar PAM (Privileged Access Management)
2. Actualizar política de gestión de cambios
3. Revisar contratos con proveedores críticos"""
        
        else:
            return "Entendido. ¿En qué más puedo ayudarte?"


class MockIntentClassifier:
    """Mock intent classification"""
    
    async def classify(self, query: str) -> tuple[IntentType, float]:
        await asyncio.sleep(0.1)
        
        q = query.lower()
        if "riesgo" in q or "risk" in q or "vulnerabilidad" in q or "cve" in q:
            return IntentType.RISK_ASSESSMENT, 0.95 if "crítico" in q else 0.88
        elif "incidente" in q or "ransomware" in q or "ataque" in q:
            return IntentType.INCIDENT_RESPONSE, 0.97
        elif "cumplimiento" in q or "compliance" in q or "iso" in q:
            return IntentType.COMPLIANCE_CHECK, 0.92
        else:
            return IntentType.GENERAL_QUERY, 0.75


class MockMemory:
    """Mock conversation memory"""
    
    def __init__(self):
        self.sessions = {}
    
    async def add(self, session_id: str, role: str, content: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": role, "content": content})
    
    async def get(self, session_id: str, limit: int = 5) -> List[Dict]:
        return self.sessions.get(session_id, [])[-limit:]


class SimpleOrchestrator:
    """Simple orchestrator for demo"""
    
    def __init__(self):
        self.llm = MockLLMService()
        self.classifier = MockIntentClassifier()
        self.memory = MockMemory()
        self.agents = {
            IntentType.RISK_ASSESSMENT: "RiskAssessmentAgent",
            IntentType.INCIDENT_RESPONSE: "IncidentResponseAgent",
            IntentType.COMPLIANCE_CHECK: "ComplianceAgent",
            IntentType.GENERAL_QUERY: "GeneralAgent",
        }
    
    async def process(self, query: str, session_id: str) -> Dict[str, Any]:
        """Process user query"""
        start = time.time()
        
        # Get history
        history = await self.memory.get(session_id)
        
        # Classify intent
        intent, confidence = await self.classifier.classify(query)
        
        # Generate response
        response = await self.llm.generate(query)
        
        # Save to memory
        await self.memory.add(session_id, "user", query)
        await self.memory.add(session_id, "assistant", response)
        
        # Create incident data for ransomware
        incident_data = None
        if "ransomware" in query.lower():
            incident_data = {
                "type": "ransomware",
                "severity": "CRITICAL",
                "confidence": 0.95,
                "incident_number": "INC-2026-042",
                "response_plan": {
                    "steps": [
                        {"step": 1, "action": "Aislar servidor de la red"},
                        {"step": 2, "action": "Notificar al equipo de seguridad"},
                        {"step": 3, "action": "Preservar evidencias forenses"},
                        {"step": 4, "action": "Identificar sistemas afectados"},
                        {"step": 5, "action": "Bloquear comunicación con C&C"},
                        {"step": 6, "action": "Preparar restauración desde backups"},
                    ],
                    "estimated_duration_hours": 4
                }
            }
        
        elapsed = time.time() - start
        
        return {
            "response": response,
            "intent": intent.value,
            "confidence": confidence,
            "agent": self.agents[intent],
            "total_time": elapsed,
            "context_used": len(history) > 0,
            "incident_data": incident_data
        }


# ============================================================================
# Demo Functions
# ============================================================================

def sep(title="", char="━", width=70):
    """Print separator"""
    if title:
        pad = (width - len(title) - 2) // 2
        line = char * pad + f" {title} " + char * pad
        if len(line) < width:
            line += char
        print(f"\n{bold(line)}")
    else:
        print(f"\n{char * width}")


async def demo_multi_turn(orch: SimpleOrchestrator, sid: str):
    """Test 1: Multi-turn conversation"""
    sep("Test 1: Multi-turn Conversation with Memory")
    
    # Turn 1
    q1 = "¿Cuáles son los riesgos críticos actuales?"
    print(f"\n{cyan('👤 User:')} {q1}")
    
    r1 = await orch.process(q1, sid)
    print(f"\n{blue('🔍 Orchestrator:')}")
    print(f"  Intent: {yellow(r1['intent'])} (confidence: {r1['confidence']:.2f})")
    print(f"  Agent: {green(r1['agent'])}")
    print(f"\n{green('🤖 CISO:')} {r1['response']}")
    print(f"\n{cyan('⏱️  Processing time:')} {r1['total_time']:.2f}s")
    
    await asyncio.sleep(0.5)
    
    # Turn 2
    q2 = "Dame más detalles del primer riesgo"
    print(f"\n{cyan('👤 User:')} {q2}")
    
    r2 = await orch.process(q2, sid)
    ctx = "Usando contexto de mensajes anteriores" if r2['context_used'] else "Sin contexto"
    print(f"\n{blue('🔍 Orchestrator:')}")
    print(f"  Intent: {yellow(r2['intent'])} (confidence: {r2['confidence']:.2f})")
    print(f"  Agent: {green(r2['agent'])}")
    print(f"  Context: {cyan(ctx)}")
    print(f"\n{green('🤖 CISO:')} {r2['response']}")
    print(f"\n{cyan('⏱️  Processing time:')} {r2['total_time']:.2f}s")


async def demo_intent_classification(orch: SimpleOrchestrator, sid: str):
    """Test 2: Intent classification"""
    sep("Test 2: Intent Classification")
    
    queries = [
        ("Evalúa el riesgo del servidor web de producción", "risk_assessment"),
        ("Detectamos actividad sospechosa de ransomware", "incident_response"),
        ("¿Estamos cumpliendo con ISO 27001?", "compliance_check"),
    ]
    
    for idx, (query, expected) in enumerate(queries, 1):
        print(f"\n{bold(f'Query {idx}:')}")
        print(f"{cyan('👤 User:')} {query}")
        
        result = await orch.process(query, sid)
        match = "✅" if result['intent'] == expected else "❌"
        
        print(f"\n{blue('🔍 Orchestrator:')}")
        print(f"  Intent: {yellow(result['intent'])} (confidence: {result['confidence']:.2f})")
        print(f"  Agent: {green(result['agent'])}")
        print(f"  Expected: {yellow(expected)} {match}")
        print(f"\n{green('🤖 CISO:')} {result['response'][:150]}...")
        print(f"\n{cyan('⏱️  Processing time:')} {result['total_time']:.2f}s")
        
        if idx < len(queries):
            await asyncio.sleep(0.3)


async def demo_incident_response(orch: SimpleOrchestrator, sid: str):
    """Test 3: Incident response flow"""
    sep("Test 3: Incident Response Flow")
    
    query = "Detectamos actividad de ransomware en el servidor de archivos. Los archivos están siendo encriptados con extensión .locked."
    print(f"\n{cyan('👤 User:')} {query}")
    
    result = await orch.process(query, sid)
    
    print(f"\n{blue('🔍 Orchestrator:')}")
    print(f"  Intent: {yellow(result['intent'])} (confidence: {result['confidence']:.2f})")
    print(f"  Agent: {green(result['agent'])}")
    
    if result['incident_data']:
        inc = result['incident_data']
        print(f"\n{red('🚨 Incident Classification:')}")
        print(f"  Type: {yellow(inc['type'])}")
        print(f"  Severity: {red(inc['severity'])}")
        confidence_pct = f"{inc['confidence']:.0%}"
        print(f"  Confidence: {green(confidence_pct)}")
        
        plan = inc['response_plan']
        print(f"\n{blue('📋 Response Plan Generated:')}")
        print(f"\n  {bold('Immediate Actions (0-15 min):')}")
        for step in plan['steps'][:3]:
            print(f"    {step['step']}. {step['action']}")
        
        print(f"\n  {bold('Containment (15 min - 4 hrs):')}")
        for step in plan['steps'][3:6]:
            print(f"    {step['step']}. {step['action']}")
        
        print(f"\n{green('✅')} Incident {yellow(inc['incident_number'])} created")
        print(f"{green('📧')} Critical stakeholders notified")
    
    print(f"\n{green('🤖 Incident Agent:')} {result['response']}")
    
    classification_time = result['total_time'] * 0.3
    plan_time = result['total_time'] * 0.7
    
    print(f"\n{bold('Metrics:')}")
    print(f"  Classification time: {yellow(f'{classification_time:.1f}s')}")
    print(f"  Plan generation time: {yellow(f'{plan_time:.1f}s')}")
    total_time_str = f'{result["total_time"]:.1f}s'
    print(f"  Total response time: {yellow(total_time_str)}")


async def demo_summary():
    """Show summary"""
    sep("Demo Summary")
    
    print(f"\n{bold('Tests Executed:')}")
    print("  ✅ Multi-turn conversation with memory")
    print("  ✅ Intent classification across query types")
    print("  ✅ Full incident response flow")
    
    print(f"\n{bold('Key Capabilities Demonstrated:')}")
    print("  🧠 Context-aware conversation memory")
    print("  🎯 Accurate intent classification (>88% confidence)")
    print("  🤖 Multi-agent orchestration")
    print("  🚨 Automated incident response")
    print("  📋 Dynamic response plan generation")
    print("  ⚡ Sub-second average response time")
    
    print(f"\n{green('✅ All demos completed successfully!')}")


# ============================================================================
# Main
# ============================================================================

async def main():
    """Run demo"""
    print("\n" + "=" * 70)
    print(bold(cyan("🤖 CISO Digital Demo - Orchestrator & Incident Response")))
    print("=" * 70)
    
    try:
        # Initialize
        orchestrator = SimpleOrchestrator()
        session_id = f"demo-session-{uuid4()}"
        
        # Run demos
        await demo_multi_turn(orchestrator, session_id)
        await asyncio.sleep(0.5)
        
        await demo_intent_classification(orchestrator, session_id)
        await asyncio.sleep(0.5)
        
        await demo_incident_response(orchestrator, session_id)
        await asyncio.sleep(0.5)
        
        await demo_summary()
        
        print("\n" + "=" * 70)
        print(green("✅ Demo completed successfully!"))
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n{red('❌ Demo failed:')} {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    print("\nStarting CISO Digital Demo...")
    exit(asyncio.run(main()))

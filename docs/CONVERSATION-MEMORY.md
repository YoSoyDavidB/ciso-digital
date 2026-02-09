# Conversation Memory System - Technical Documentation

**Version:** 1.0  
**Last Updated:** 2026-02-06  
**Status:** Production Ready  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Window Size & Context Management](#window-size--context-management)
4. [Semantic Search](#semantic-search)
5. [Privacy & Data Retention](#privacy--data-retention)
6. [API Reference](#api-reference)
7. [Usage Examples](#usage-examples)
8. [Best Practices](#best-practices)

---

## 🎯 Overview

The **Conversation Memory System** enables the CISO Digital assistant to maintain context across multiple turns of conversation. It provides:

- ✅ **Short-term Memory**: Recent conversation history
- ✅ **Long-term Memory**: Semantic search across all conversations
- ✅ **Context Management**: Intelligent window sizing and token limits
- ✅ **Privacy Controls**: Automatic PII detection and retention policies
- ✅ **Embeddings**: Vector representations for semantic search

### Architecture Components

```
┌─────────────────────────────────────────────────────────┐
│              Conversation Memory System                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │         PostgreSQL (Structured Storage)           │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  conversations                               │ │  │
│  │  │  ├─ id (UUID)                                │ │  │
│  │  │  ├─ session_id (VARCHAR)                     │ │  │
│  │  │  ├─ user_id (VARCHAR)                        │ │  │
│  │  │  ├─ role (user | assistant)                  │ │  │
│  │  │  ├─ content (TEXT)                           │ │  │
│  │  │  ├─ timestamp (TIMESTAMPTZ)                  │ │  │
│  │  │  ├─ metadata (JSONB)                         │ │  │
│  │  │  └─ embedding_id (VARCHAR) → Qdrant         │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↕                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │          Qdrant (Vector Storage)                  │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  conversations_collection                    │ │  │
│  │  │  ├─ id (matches PostgreSQL)                  │ │  │
│  │  │  ├─ vector (embedding)                       │ │  │
│  │  │  ├─ payload:                                 │ │  │
│  │  │  │  ├─ session_id                            │ │  │
│  │  │  │  ├─ user_id                               │ │  │
│  │  │  │  ├─ content                               │ │  │
│  │  │  │  ├─ role                                  │ │  │
│  │  │  │  └─ timestamp                             │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 How It Works

### 1. Storing Messages

When a user sends a message and receives a response:

```python
from app.services.conversation_memory import ConversationMemoryService

# Initialize service
memory = ConversationMemoryService(
    db_session=db_session,
    rag_service=rag_service
)

# Store user message
await memory.add_message(
    session_id="sess-abc-123",
    role="user",
    content="¿Cuáles son los riesgos críticos en el servidor web?",
    user_id="user-456",
    metadata={
        "client_ip": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "intent": "risk_assessment"
    }
)

# Store assistant response
await memory.add_message(
    session_id="sess-abc-123",
    role="assistant",
    content="Identifiqué 3 riesgos críticos...",
    user_id="user-456",
    metadata={
        "agent_used": "RiskAssessmentAgent",
        "confidence": 0.95,
        "processing_time_ms": 1234,
        "sources": ["knowledge_base", "recent_scans"]
    }
)
```

**What happens internally:**
1. Message saved to PostgreSQL with timestamp
2. Embedding created using OpenAI/Anthropic API
3. Embedding stored in Qdrant with metadata
4. Message appears in conversation history

### 2. Retrieving History

```python
# Get recent messages for context
history = await memory.get_history(
    session_id="sess-abc-123",
    limit=5  # Last 5 messages
)

# Result: List[ConversationMessage]
for msg in history:
    print(f"{msg.role}: {msg.content}")
    print(f"  Timestamp: {msg.timestamp}")
    print(f"  Metadata: {msg.metadata}")
```

### 3. Semantic Search

```python
# Find similar conversations
similar = await memory.search_similar_conversations(
    query="problemas con servidor web",
    user_id="user-456",  # Optional: limit to user's conversations
    limit=3,
    min_score=0.7
)

# Results ranked by semantic similarity
for conv in similar:
    print(f"Score: {conv.score:.2f}")
    print(f"Content: {conv.content}")
    print(f"Session: {conv.session_id}")
```

### 4. Context Window Management

```python
# Get context with token limit
context = await memory.get_context_for_llm(
    session_id="sess-abc-123",
    max_tokens=2000  # Leave room for system prompt + response
)

# Result: Optimized message list that fits in token budget
# Older messages may be summarized or excluded
```

---

## 🪟 Window Size & Context Management

### Default Configuration

```python
# app/core/config.py

class Settings(BaseSettings):
    # Conversation memory settings
    CONVERSATION_WINDOW_SIZE: int = 10  # Messages to keep in short-term memory
    CONVERSATION_MAX_TOKENS: int = 4000  # Max tokens for context
    CONVERSATION_SUMMARY_THRESHOLD: int = 20  # Summarize after N messages
    CONVERSATION_RETENTION_DAYS: int = 90  # Keep conversations for 90 days
```

### Adaptive Window Sizing

The system dynamically adjusts the context window based on:

1. **Token Budget**: Available tokens for the LLM call
2. **Relevance**: More recent messages have higher priority
3. **Importance**: Messages with high confidence/relevance kept longer
4. **Turn Boundaries**: Complete turns (user + assistant) kept together

```python
async def get_adaptive_context(
    self,
    session_id: str,
    max_tokens: int,
    importance_threshold: float = 0.5
) -> List[ConversationMessage]:
    """Get context with adaptive window sizing."""
    
    # Get all messages for session
    all_messages = await self.get_history(session_id, limit=100)
    
    # Calculate importance scores
    scored_messages = [
        (msg, self._calculate_importance(msg))
        for msg in all_messages
    ]
    
    # Sort by importance (recent messages get bonus)
    scored_messages.sort(
        key=lambda x: (x[1], x[0].timestamp),
        reverse=True
    )
    
    # Add messages until token budget exhausted
    selected = []
    total_tokens = 0
    
    for msg, importance in scored_messages:
        msg_tokens = self._count_tokens(msg.content)
        
        if total_tokens + msg_tokens <= max_tokens:
            selected.append(msg)
            total_tokens += msg_tokens
        elif importance > importance_threshold:
            # Important message: summarize instead of drop
            summary = await self._summarize_message(msg)
            summary_tokens = self._count_tokens(summary)
            
            if total_tokens + summary_tokens <= max_tokens:
                selected.append(ConversationMessage(
                    **msg.dict(),
                    content=summary,
                    metadata={**msg.metadata, "summarized": True}
                ))
                total_tokens += summary_tokens
    
    # Sort by timestamp for chronological order
    selected.sort(key=lambda m: m.timestamp)
    
    return selected
```

### Conversation Summarization

When conversations get long, automatic summarization kicks in:

```python
async def summarize_conversation(
    self,
    session_id: str,
    start_index: int = 0,
    end_index: Optional[int] = None
) -> str:
    """Summarize a portion of the conversation."""
    
    messages = await self.get_history(session_id, limit=None)
    
    if end_index is None:
        end_index = len(messages)
    
    to_summarize = messages[start_index:end_index]
    
    # Create summary prompt
    conversation_text = "\n".join([
        f"{msg.role}: {msg.content}"
        for msg in to_summarize
    ])
    
    summary_prompt = f"""
    Summarize this conversation concisely, preserving key information:
    
    {conversation_text}
    
    Summary:
    """
    
    summary = await self.llm_service.generate(summary_prompt)
    
    # Store summary as special message
    await self.add_message(
        session_id=session_id,
        role="system",
        content=summary,
        user_id=to_summarize[0].user_id,
        metadata={
            "type": "summary",
            "messages_summarized": len(to_summarize),
            "start_index": start_index,
            "end_index": end_index
        }
    )
    
    return summary
```

---

## 🔍 Semantic Search

### How Semantic Search Works

1. **Query Embedding**: User's query converted to vector
2. **Vector Search**: Qdrant finds similar conversations
3. **Filtering**: Apply user_id, date range, session filters
4. **Ranking**: Sort by similarity score
5. **Formatting**: Return with context

```python
async def search_similar_conversations(
    self,
    query: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 5,
    min_score: float = 0.7
) -> List[ConversationSearchResult]:
    """
    Search for similar conversations using semantic search.
    
    Args:
        query: Search query in natural language
        user_id: Optional filter by user
        session_id: Optional filter by session
        date_from: Optional start date filter
        date_to: Optional end date filter
        limit: Maximum results to return
        min_score: Minimum similarity score (0.0-1.0)
    
    Returns:
        List of ConversationSearchResult with similarity scores
    """
    
    # Create embedding for query
    query_embedding = await self.rag_service.create_embedding(query)
    
    # Build Qdrant filter
    qdrant_filter = self._build_filter(
        user_id=user_id,
        session_id=session_id,
        date_from=date_from,
        date_to=date_to
    )
    
    # Search in Qdrant
    search_results = await self.rag_service.search(
        collection_name="conversations",
        query_vector=query_embedding,
        filter=qdrant_filter,
        limit=limit,
        score_threshold=min_score
    )
    
    # Fetch full messages from PostgreSQL
    message_ids = [r.id for r in search_results]
    messages = await self._fetch_messages_by_ids(message_ids)
    
    # Combine results
    results = []
    for qdrant_result, message in zip(search_results, messages):
        results.append(ConversationSearchResult(
            message=message,
            score=qdrant_result.score,
            highlights=self._extract_highlights(query, message.content)
        ))
    
    return results
```

### Search Examples

#### Example 1: Find Previous Discussions

```python
# User asks: "¿Hablamos antes sobre riesgos en AWS?"

similar = await memory.search_similar_conversations(
    query="riesgos AWS configuración",
    user_id=current_user_id,
    limit=3
)

if similar:
    context_msg = "Sí, encontré estas conversaciones previas:\n"
    for result in similar:
        context_msg += f"\n- {result.message.timestamp}: {result.message.content[:100]}..."
    
    # Include in LLM prompt for more informed response
```

#### Example 2: Find Similar Issues

```python
# User reports: "El servidor web está lento"

# Search for similar issues
similar_issues = await memory.search_similar_conversations(
    query="servidor web lento rendimiento",
    date_from=datetime.now() - timedelta(days=30),  # Last 30 days
    limit=5
)

# Check if there's a known solution
if similar_issues:
    past_solutions = [
        r.message.metadata.get("resolution")
        for r in similar_issues
        if "resolution" in r.message.metadata
    ]
    
    # Suggest previously successful solutions
```

---

## 🔒 Privacy & Data Retention

### PII Detection

Automatic detection and handling of Personally Identifiable Information:

```python
from app.services.pii_detector import PIIDetector

class ConversationMemoryService:
    def __init__(self, ...):
        self.pii_detector = PIIDetector()
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: str,
        metadata: Optional[Dict] = None
    ):
        """Add message with PII detection."""
        
        # Detect PII in content
        pii_results = self.pii_detector.detect(content)
        
        if pii_results.has_pii:
            # Option 1: Redact PII
            redacted_content = self.pii_detector.redact(content)
            
            # Option 2: Encrypt PII
            encrypted_content = self.pii_detector.encrypt(content)
            
            # Store metadata about PII
            metadata = metadata or {}
            metadata["pii_detected"] = True
            metadata["pii_types"] = [p.type for p in pii_results.entities]
            
            # Use redacted version
            content = redacted_content
        
        # Continue with normal storage
        ...
```

### Supported PII Types

```python
class PIIType(Enum):
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    PASSPORT = "passport"
    LICENSE = "driver_license"
```

### Data Retention Policies

```python
# app/features/conversation/retention.py

class RetentionPolicy:
    """Defines conversation data retention policy."""
    
    # Default retention: 90 days
    DEFAULT_RETENTION_DAYS = 90
    
    # Critical incidents: 7 years
    INCIDENT_RETENTION_DAYS = 365 * 7
    
    # Compliance records: 7 years
    COMPLIANCE_RETENTION_DAYS = 365 * 7
    
    # General queries: 30 days
    GENERAL_RETENTION_DAYS = 30

async def apply_retention_policy():
    """Clean up old conversations based on retention policy."""
    
    now = datetime.now(timezone.utc)
    
    # General conversations
    await db.execute(
        delete(ConversationMessage)
        .where(
            and_(
                ConversationMessage.metadata["type"] == "general",
                ConversationMessage.timestamp < now - timedelta(days=30)
            )
        )
    )
    
    # Incident-related conversations
    await db.execute(
        delete(ConversationMessage)
        .where(
            and_(
                ConversationMessage.metadata["type"] == "incident",
                ConversationMessage.timestamp < now - timedelta(days=365*7)
            )
        )
    )
    
    # Also clean up Qdrant vectors
    await qdrant_client.delete(
        collection_name="conversations",
        points_selector=FilterSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key="timestamp",
                        range=Range(
                            lt=now - timedelta(days=30)
                        )
                    )
                ]
            )
        )
    )
```

### User Data Deletion

GDPR/CCPA compliance - delete user data on request:

```python
async def delete_user_conversations(
    self,
    user_id: str,
    verify: bool = True
) -> Dict[str, int]:
    """
    Delete all conversations for a user (GDPR/CCPA compliance).
    
    Args:
        user_id: User identifier
        verify: Require confirmation before deletion
    
    Returns:
        Dictionary with deletion statistics
    """
    
    if verify:
        # Require explicit confirmation
        confirmation = input(
            f"Delete ALL conversations for user {user_id}? (yes/no): "
        )
        if confirmation.lower() != "yes":
            raise ValueError("Deletion cancelled by user")
    
    # Get all message IDs for user
    messages = await self.db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.user_id == user_id)
    )
    message_ids = [m.id for m in messages.scalars().all()]
    
    # Delete from Qdrant
    qdrant_deleted = await self.rag_service.delete_points(
        collection_name="conversations",
        points_ids=message_ids
    )
    
    # Delete from PostgreSQL
    result = await self.db.execute(
        delete(ConversationMessage)
        .where(ConversationMessage.user_id == user_id)
    )
    
    await self.db.commit()
    
    return {
        "user_id": user_id,
        "messages_deleted": result.rowcount,
        "embeddings_deleted": qdrant_deleted
    }
```

---

## 🔌 API Reference

### ConversationMemoryService

```python
class ConversationMemoryService:
    """Service for managing conversation memory."""
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationMessage:
        """Add a message to conversation history."""
        ...
    
    async def get_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[ConversationMessage]:
        """Get recent conversation history."""
        ...
    
    async def search_similar_conversations(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 5,
        min_score: float = 0.7
    ) -> List[ConversationSearchResult]:
        """Search for semantically similar conversations."""
        ...
    
    async def get_context_for_llm(
        self,
        session_id: str,
        max_tokens: int = 2000
    ) -> List[ConversationMessage]:
        """Get optimized context for LLM call."""
        ...
    
    async def summarize_conversation(
        self,
        session_id: str,
        start_index: int = 0,
        end_index: Optional[int] = None
    ) -> str:
        """Summarize a portion of conversation."""
        ...
    
    async def delete_session(
        self,
        session_id: str
    ) -> int:
        """Delete all messages in a session."""
        ...
    
    async def delete_user_conversations(
        self,
        user_id: str,
        verify: bool = True
    ) -> Dict[str, int]:
        """Delete all conversations for a user."""
        ...
```

---

## 💡 Usage Examples

### Example 1: Basic Chat with Context

```python
from app.services.conversation_memory import ConversationMemoryService

# Initialize
memory = ConversationMemoryService(db_session, rag_service)
session_id = "sess-abc-123"
user_id = "user-456"

# User's first message
await memory.add_message(
    session_id=session_id,
    role="user",
    content="¿Cuáles son nuestros riesgos críticos?",
    user_id=user_id
)

# Get context for LLM
history = await memory.get_history(session_id, limit=5)

# Generate response (with context)
response = await orchestrator.process_request(
    user_query="¿Cuáles son nuestros riesgos críticos?",
    session_id=session_id,
    user_id=user_id
)

# Store assistant response
await memory.add_message(
    session_id=session_id,
    role="assistant",
    content=response.response,
    user_id=user_id,
    metadata={
        "agent": response.agent_used,
        "confidence": response.confidence
    }
)

# User's follow-up (using context)
await memory.add_message(
    session_id=session_id,
    role="user",
    content="Dame más detalles del primero",  # Refers to previous message
    user_id=user_id
)

# Orchestrator retrieves history automatically
response2 = await orchestrator.process_request(
    user_query="Dame más detalles del primero",
    session_id=session_id,
    user_id=user_id
)
# → Understands "del primero" from context
```

### Example 2: Search Previous Conversations

```python
# User asks if something was discussed before
query = "¿Ya hablamos de la vulnerabilidad en Apache?"

# Search previous conversations
similar = await memory.search_similar_conversations(
    query="vulnerabilidad Apache Struts",
    user_id=user_id,
    limit=3,
    min_score=0.75
)

if similar:
    # Found previous discussion
    print("Sí, encontré estas conversaciones:")
    for result in similar:
        print(f"- {result.message.timestamp}: {result.message.content[:100]}")
        print(f"  Relevancia: {result.score:.0%}")
else:
    print("No encontré conversaciones previas sobre ese tema")
```

### Example 3: Long Conversation Summary

```python
# After 20 messages, summarize older portion
history = await memory.get_history(session_id, limit=None)

if len(history) > 20:
    # Summarize first 15 messages
    summary = await memory.summarize_conversation(
        session_id=session_id,
        start_index=0,
        end_index=15
    )
    
    print(f"Summary: {summary}")
    
    # Use summary + recent messages for context
    recent_messages = history[15:]
    
    context = [
        ConversationMessage(
            session_id=session_id,
            role="system",
            content=f"Resumen de conversación previa: {summary}",
            user_id=user_id,
            timestamp=history[14].timestamp
        ),
        *recent_messages
    ]
```

---

## ✅ Best Practices

### 1. Session Management

**DO:**
- ✅ Create new session for each conversation
- ✅ Use descriptive session IDs (`sess-{user_id}-{timestamp}`)
- ✅ Associate sessions with users
- ✅ Clean up abandoned sessions

**DON'T:**
- ❌ Reuse session IDs across users
- ❌ Keep sessions active indefinitely
- ❌ Mix unrelated topics in same session
- ❌ Forget to close sessions

### 2. Context Window

**DO:**
- ✅ Limit context to relevant messages
- ✅ Summarize long conversations
- ✅ Monitor token usage
- ✅ Prioritize recent and important messages

**DON'T:**
- ❌ Send entire conversation history every time
- ❌ Exceed LLM token limits
- ❌ Include irrelevant context
- ❌ Forget to paginate long histories

### 3. Privacy

**DO:**
- ✅ Detect and redact PII
- ✅ Implement data retention policies
- ✅ Provide user data deletion
- ✅ Encrypt sensitive data

**DON'T:**
- ❌ Store PII without redaction
- ❌ Keep data indefinitely
- ❌ Ignore GDPR/CCPA requirements
- ❌ Share conversations between users

### 4. Performance

**DO:**
- ✅ Index frequently queried fields
- ✅ Cache recent conversations
- ✅ Use connection pooling
- ✅ Batch operations when possible

**DON'T:**
- ❌ Query all messages for every request
- ❌ Create embeddings synchronously
- ❌ Skip database indexes
- ❌ Ignore slow queries

---

## 📊 Monitoring

### Key Metrics

```python
# Track these metrics
metrics = {
    "memory.messages_stored_total": Counter,
    "memory.messages_retrieved_total": Counter,
    "memory.search_queries_total": Counter,
    "memory.search_duration_seconds": Histogram,
    "memory.embeddings_created_total": Counter,
    "memory.context_window_size": Gauge,
    "memory.storage_size_bytes": Gauge,
}
```

### Health Checks

```python
async def check_memory_health() -> HealthStatus:
    """Check conversation memory system health."""
    
    checks = {
        "postgres": await check_postgres_connection(),
        "qdrant": await check_qdrant_connection(),
        "embeddings": await check_embedding_service(),
        "storage_usage": await check_storage_usage()
    }
    
    return HealthStatus(
        healthy=all(checks.values()),
        checks=checks
    )
```

---

## 🔗 Related Documentation

- [CISO Orchestrator](./ORCHESTRATOR.md)
- [Incident Response](./INCIDENT-RESPONSE.md)
- [RAG System](./RAG-SYSTEM.md)
- [API Documentation](./API.md)

---

**Maintained by:** CISO Digital Development Team  
**Last Review:** 2026-02-06  
**Next Review:** 2026-03-06

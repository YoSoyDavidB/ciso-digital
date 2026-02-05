"""
Embedding Service for generating vector embeddings.

Supports Azure OpenAI text-embedding-3-small (primary) with OpenAI and
local sentence-transformers fallback.
"""

import logging
from functools import lru_cache

from app.core.config import settings


logger = logging.getLogger(__name__)


# Import Azure OpenAI at module level for proper mocking in tests
try:
    from openai import AsyncAzureOpenAI, AsyncOpenAI, OpenAIError
except ImportError:
    AsyncAzureOpenAI = None  # type: ignore
    AsyncOpenAI = None  # type: ignore
    OpenAIError = Exception  # type: ignore

# Import SentenceTransformer at module level for proper mocking
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None  # type: ignore


class EmbeddingService:
    """
    Service for generating text embeddings.

    Priority order:
    1. Azure OpenAI (primary) - text-embedding-3-small (1536-dim)
    2. OpenAI (fallback) - text-embedding-3-large (1536-dim)
    3. Local sentence-transformers (fallback) - all-mpnet-base-v2 (768-dim)

    Implements caching and batching for efficiency.
    """

    def __init__(self):
        """Initialize embedding service with Azure OpenAI or fallbacks."""
        self.using_azure = False
        self.using_openai = False
        self.using_local = False
        self.cache: dict[str, list[float]] = {}
        self._model = None
        self._dimension = 0
        self.client = None

        # Try Azure OpenAI first (primary)
        if self._try_initialize_azure():
            return
        
        # Fallback to OpenAI
        if self._try_initialize_openai():
            return
        
        # Last fallback to local
        logger.info("No cloud API available, using local embeddings")
        self._initialize_local()

    def _try_initialize_azure(self) -> bool:
        """Try to initialize Azure OpenAI client."""
        if not all([
            settings.AZURE_OPENAI_KEY,
            settings.AZURE_OPENAI_ENDPOINT,
            settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            AsyncAzureOpenAI
        ]):
            return False
        
        try:
            self.client = AsyncAzureOpenAI(
                api_key=settings.AZURE_OPENAI_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.model_name = settings.AZURE_OPENAI_EMBEDDING_MODEL
            self.deployment_name = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
            
            # text-embedding-3-small has 1536 dimensions
            self._dimension = 1536
            self.using_azure = True
            logger.info(
                f"✅ EmbeddingService initialized with Azure OpenAI: {self.deployment_name} "
                f"(model: {self.model_name}, {self._dimension}-dim)"
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize Azure OpenAI: {e}")
            return False

    def _try_initialize_openai(self) -> bool:
        """Try to initialize OpenAI client."""
        if not settings.OPENAI_API_KEY or not AsyncOpenAI:
            return False
        
        try:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model_name = "text-embedding-3-large"
            self._dimension = 1536
            self.using_openai = True
            logger.info(
                f"EmbeddingService initialized with OpenAI model: {self.model_name}"
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI: {e}")
            return False

    def _initialize_local(self):
        """Initialize local sentence-transformers model."""
        if SentenceTransformer is None:
            logger.error("sentence-transformers not available")
            raise ImportError("sentence-transformers package is required for local embeddings")

        try:
            self._model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
            self.model_name = "all-mpnet-base-v2"
            self._dimension = 768
            self.using_local = True
            logger.info(
                f"EmbeddingService initialized with local model: {self.model_name}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize local embeddings: {e}")
            raise

    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector

        Example:
            >>> service = EmbeddingService()
            >>> embedding = await service.embed("Hello world")
            >>> len(embedding)
            1536  # or 768 for local
        """
        # Check cache first
        if text in self.cache:
            logger.debug(f"Cache hit for text: {text[:50]}...")
            return self.cache[text]

        logger.info(f"Generating embedding for text: {text[:50]}...")

        if self.using_azure or self.using_openai:
            embedding = await self._embed_cloud(text)
        else:
            embedding = self._embed_local(text)

        # Cache the result
        self.cache[text] = embedding

        logger.info(
            f"Generated embedding with dimension: {len(embedding)} "
            f"using {'Azure' if self.using_azure else 'OpenAI' if self.using_openai else 'local'} model"
        )

        return embedding

    async def _embed_cloud(self, text: str) -> list[float]:
        """Generate embedding using Azure OpenAI or OpenAI API."""
        if self.client is None:
            raise RuntimeError("Cloud client not initialized")

        try:
            # For Azure, we need to pass the deployment name
            if self.using_azure:
                response = await self.client.embeddings.create(
                    model=self.deployment_name,  # Azure uses deployment name
                    input=text
                )
            else:
                # OpenAI uses model name directly
                response = await self.client.embeddings.create(
                    model=self.model_name,
                    input=text
                )
            return response.data[0].embedding
        except OpenAIError as e:
            logger.error(f"Cloud embedding error: {e}")
            raise

    def _embed_local(self, text: str) -> list[float]:
        """Generate embedding using local model."""
        if self._model is None:
            raise RuntimeError("Local model not initialized")

        embedding = self._model.encode(text, convert_to_numpy=True)
        # Handle both list and numpy array responses (for testing)
        if isinstance(embedding, list):
            return embedding[0] if embedding and isinstance(embedding[0], list) else embedding
        return embedding.tolist()

    async def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 100
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts efficiently.

        Implements caching and automatic batching for large inputs.

        Args:
            texts: List of texts to embed
            batch_size: Maximum number of texts per batch (default: 100)

        Returns:
            List of embedding vectors, one per input text

        Example:
            >>> service = EmbeddingService()
            >>> embeddings = await service.embed_batch(["Hello", "World"])
            >>> len(embeddings)
            2
            >>> len(embeddings[0])
            1536  # or 768 for local
        """
        if not texts:
            return []

        logger.info(f"Generating embeddings for {len(texts)} texts in batches of {batch_size}")

        embeddings: list[list[float]] = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await self._process_batch(batch)
            embeddings.extend(batch_embeddings)

            logger.debug(f"Processed batch {i // batch_size + 1}, total embeddings: {len(embeddings)}")

        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings

    async def _process_batch(self, texts: list[str]) -> list[list[float]]:
        """Process a single batch of texts."""
        # Check cache for each text
        embeddings: list[list[float] | None] = []
        uncached_indices: list[int] = []
        uncached_texts: list[str] = []

        for idx, text in enumerate(texts):
            if text in self.cache:
                embeddings.append(self.cache[text])
                logger.debug(f"Cache hit for text {idx}")
            else:
                embeddings.append(None)
                uncached_indices.append(idx)
                uncached_texts.append(text)

        # Generate embeddings for uncached texts
        if uncached_texts:
            if self.using_azure or self.using_openai:
                new_embeddings = await self._embed_batch_cloud(uncached_texts)
            else:
                new_embeddings = self._embed_batch_local(uncached_texts)

            # Insert new embeddings and cache them
            for idx, embedding in zip(uncached_indices, new_embeddings, strict=False):
                embeddings[idx] = embedding
                self.cache[texts[idx]] = embedding

        return embeddings  # type: ignore

    async def _embed_batch_cloud(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch using Azure OpenAI or OpenAI API."""
        if self.client is None:
            raise RuntimeError("Cloud client not initialized")

        try:
            # For Azure, we need to pass the deployment name
            if self.using_azure:
                response = await self.client.embeddings.create(
                    model=self.deployment_name,  # Azure uses deployment name
                    input=texts
                )
            else:
                # OpenAI uses model name directly
                response = await self.client.embeddings.create(
                    model=self.model_name,
                    input=texts
                )
            return [data.embedding for data in response.data]
        except OpenAIError as e:
            logger.error(f"Cloud batch embedding error: {e}")
            raise

    def _embed_batch_local(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch using local model."""
        if self._model is None:
            raise RuntimeError("Local model not initialized")

        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]

    @property
    def dimension(self) -> int:
        """Get the dimension of embeddings produced by this service."""
        return self._dimension


# Singleton instance
_embedding_service: EmbeddingService | None = None


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """
    Get or create singleton EmbeddingService instance.

    Returns:
        EmbeddingService: The singleton embedding service

    Example:
        >>> service = get_embedding_service()
        >>> embedding = await service.embed("Hello world")
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

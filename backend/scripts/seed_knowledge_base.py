#!/usr/bin/env python
"""
Script para popular la base de conocimiento vectorial (Qdrant).

Este script:
1. Lee documentos markdown de knowledge-base/
2. Divide documentos en chunks con overlap
3. Genera embeddings para cada chunk
4. Guarda en Qdrant collection especificada

Uso:
    # Colección por defecto (security_knowledge)
    python scripts/seed_knowledge_base.py
    
    # Resetear colección antes de sembrar
    python scripts/seed_knowledge_base.py --reset
    
    # Sembrar un archivo específico
    python scripts/seed_knowledge_base.py --file knowledge-base/iso27001-overview.md
    
    # Sembrar playbooks en colección incident_playbooks
    python scripts/seed_knowledge_base.py --collection incident_playbooks --directory knowledge-base/playbooks/
    
    # Resetear y sembrar playbooks
    python scripts/seed_knowledge_base.py --collection incident_playbooks --directory knowledge-base/playbooks/ --reset
"""

import argparse
import asyncio
import logging
import re
import sys
from pathlib import Path
from typing import Any


# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """
    Divide un texto en chunks con overlap.

    Args:
        text: Texto a dividir
        chunk_size: Tamaño máximo de cada chunk en caracteres
        overlap: Número de caracteres de solapamiento entre chunks

    Returns:
        Lista de chunks de texto

    Example:
        >>> text = "A" * 2500
        >>> chunks = chunk_text(text, chunk_size=1000, overlap=200)
        >>> len(chunks)
        3
        >>> len(chunks[0])
        1000
    """
    if not text or not text.strip():
        return []

    # Limpiar texto
    text = text.strip()

    # Si el texto es menor que chunk_size, retornar como un solo chunk
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        # Calcular el final del chunk
        end = start + chunk_size

        # Si no es el último chunk, buscar un punto de corte natural
        if end < len(text):
            # Buscar el último punto, nueva línea o espacio antes del límite
            last_period = text.rfind(".", start, end)
            last_newline = text.rfind("\n", start, end)
            last_space = text.rfind(" ", start, end)

            # Usar el punto de corte más apropiado
            natural_break = max(last_period, last_newline, last_space)

            if natural_break > start:
                end = natural_break + 1  # Incluir el carácter de corte

        # Extraer chunk
        chunk = text[start:end].strip()

        if chunk:  # Solo agregar chunks no vacíos
            chunks.append(chunk)

        # Mover el inicio para el siguiente chunk con overlap
        start = end - overlap

        # Evitar bucle infinito si overlap es muy grande
        if start <= 0 and chunks:
            break

    logger.info(f"Text divided into {len(chunks)} chunks")
    return chunks


def extract_metadata(filepath: Path) -> dict[str, Any]:
    """
    Extrae metadata de un archivo markdown.

    Args:
        filepath: Ruta al archivo

    Returns:
        Dict con metadata del documento

    Example:
        >>> filepath = Path("knowledge-base/iso27001-overview.md")
        >>> metadata = extract_metadata(filepath)
        >>> metadata["filename"]
        'iso27001-overview.md'
        >>> metadata["document_type"]
        'standard'
    """
    filename = filepath.name
    stem = filepath.stem

    # Inferir tipo de documento desde el nombre
    document_type = "general"
    if "iso" in stem.lower() or "standard" in stem.lower():
        document_type = "standard"
    elif "playbook" in stem.lower():
        document_type = "playbook"
    elif "risk" in stem.lower():
        document_type = "risk-management"
    elif "incident" in stem.lower() and "playbook" not in stem.lower():
        document_type = "incident-response"
    elif "guide" in stem.lower():
        document_type = "guide"
    elif "policy" in stem.lower():
        document_type = "policy"
    elif "regulation" in stem.lower() or "dora" in stem.lower():
        document_type = "regulation"

    # Leer el archivo para extraer el título
    try:
        content = filepath.read_text(encoding="utf-8")
        # Buscar el primer header markdown (# Título)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else stem.replace("-", " ").title()
    except Exception as e:
        logger.warning(f"Could not read title from {filename}: {e}")
        title = stem.replace("-", " ").title()

    metadata = {
        "filename": filename,
        "document_type": document_type,
        "title": title,
        "source": f"knowledge-base/{filename}",
    }

    logger.debug(f"Extracted metadata for {filename}: {metadata}")
    return metadata


async def ingest_document(
    filepath: Path,
    embedding_service: EmbeddingService,
    vector_store: VectorStoreService,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> int:
    """
    Ingesta un documento en la base vectorial.

    Args:
        filepath: Ruta al archivo markdown
        embedding_service: Servicio de embeddings
        vector_store: Servicio de vector store
        chunk_size: Tamaño de chunks en caracteres
        overlap: Overlap entre chunks en caracteres

    Returns:
        Número de chunks ingresados

    Raises:
        FileNotFoundError: Si el archivo no existe
        Exception: Si hay error en la ingesta
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    logger.info(f"Processing document: {filepath.name}")

    # 1. Leer contenido
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        raise

    if not content.strip():
        logger.warning(f"Document {filepath.name} is empty, skipping")
        return 0

    # 2. Extraer metadata
    base_metadata = extract_metadata(filepath)

    # 3. Dividir en chunks
    chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)

    if not chunks:
        logger.warning(f"No chunks generated from {filepath.name}")
        return 0

    logger.info(f"Generated {len(chunks)} chunks from {filepath.name}")

    # 4. Generar embeddings para todos los chunks
    logger.info("Generating embeddings...")
    embeddings = await embedding_service.embed_batch(chunks)

    # 5. Preparar metadata para cada chunk
    metadata_list = []
    for i, chunk_content in enumerate(chunks):
        chunk_metadata = base_metadata.copy()
        chunk_metadata.update(
            {
                "chunk_index": i,
                "total_chunks": len(chunks),
                "text": chunk_content,  # Guardar el texto en metadata para recuperación
                "char_count": len(chunk_content),
            }
        )
        metadata_list.append(chunk_metadata)

    # 6. Insertar en Qdrant
    logger.info(f"Inserting {len(embeddings)} chunks into Qdrant...")
    try:
        await vector_store.insert_embeddings(
            embeddings=embeddings,
            metadata=metadata_list,
        )
        logger.info(
            f"✅ Successfully ingested {filepath.name}: {len(chunks)} chunks"
        )
        return len(chunks)
    except Exception as e:
        logger.error(f"Error inserting embeddings: {e}")
        raise


async def seed_knowledge_base(
    knowledge_base_dir: Path,
    reset: bool = False,
    specific_file: Path | None = None,
    chunk_size: int = 1000,
    overlap: int = 200,
    collection_name: str = "security_knowledge",
) -> dict[str, int]:
    """
    Popular la base de conocimiento completa.

    Args:
        knowledge_base_dir: Directorio con documentos markdown
        reset: Si True, resetea la colección antes de ingestar
        specific_file: Si se especifica, solo ingesta este archivo
        chunk_size: Tamaño de chunks en caracteres
        overlap: Overlap entre chunks
        collection_name: Nombre de la colección en Qdrant (default: security_knowledge)

    Returns:
        Dict con estadísticas de ingesta

    Example:
        >>> stats = await seed_knowledge_base(Path("knowledge-base"))
        >>> stats["total_documents"]
        4
        >>> stats["total_chunks"]
        42
    """
    logger.info("=" * 60)
    logger.info("🚀 Starting Knowledge Base Seeding")
    logger.info(f"📁 Collection: {collection_name}")
    logger.info(f"📂 Directory: {knowledge_base_dir}")
    logger.info("=" * 60)

    # Inicializar servicios
    logger.info("Initializing services...")
    embedding_service = EmbeddingService()
    vector_store = VectorStoreService(
        qdrant_url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        collection_name=collection_name,
    )

    # Determinar dimensión de embeddings
    embedding_dimension = embedding_service.dimension
    logger.info(f"Using embedding dimension: {embedding_dimension}")
    logger.info(f"Embedding service: {'Azure OpenAI' if embedding_service.using_azure else 'OpenAI' if embedding_service.using_openai else 'Local'}")

    # Resetear colección si se solicita
    if reset:
        logger.warning(f"⚠️  Resetting collection '{collection_name}'...")
        try:
            # Verificar si existe
            exists = await vector_store.client.collection_exists(collection_name)
            if exists:
                await vector_store.client.delete_collection(collection_name)
                logger.info("✅ Collection deleted")
        except Exception as e:
            logger.warning(f"Could not delete collection: {e}")

    # Asegurar que la colección existe
    logger.info("Ensuring collection exists...")
    await vector_store.ensure_collection(
        vector_size=embedding_dimension,
        distance="Cosine",
    )
    logger.info(f"✅ Collection ready (dimension: {embedding_dimension})")

    # Obtener lista de archivos a procesar
    if specific_file:
        files = [specific_file] if specific_file.exists() else []
    else:
        files = sorted(knowledge_base_dir.glob("*.md"))

    if not files:
        logger.error("No markdown files found to process")
        return {"total_documents": 0, "total_chunks": 0, "failed": 0}

    logger.info(f"Found {len(files)} document(s) to process")

    # Procesar cada archivo
    stats = {
        "total_documents": 0,
        "total_chunks": 0,
        "failed": 0,
        "documents": {},
    }

    for filepath in files:
        try:
            chunks_count = await ingest_document(
                filepath=filepath,
                embedding_service=embedding_service,
                vector_store=vector_store,
                chunk_size=chunk_size,
                overlap=overlap,
            )

            stats["total_documents"] += 1
            stats["total_chunks"] += chunks_count
            stats["documents"][filepath.name] = {
                "chunks": chunks_count,
                "status": "success",
            }

        except Exception as e:
            logger.error(f"❌ Failed to ingest {filepath.name}: {e}")
            stats["failed"] += 1
            stats["documents"][filepath.name] = {
                "chunks": 0,
                "status": "failed",
                "error": str(e),
            }

    # Resumen final
    logger.info("=" * 60)
    logger.info("📊 Seeding Summary")
    logger.info("=" * 60)
    logger.info(f"Total documents processed: {stats['total_documents']}")
    logger.info(f"Total chunks inserted: {stats['total_chunks']}")
    logger.info(f"Failed documents: {stats['failed']}")
    logger.info("")

    for doc_name, doc_stats in stats["documents"].items():
        status_icon = "✅" if doc_stats["status"] == "success" else "❌"
        logger.info(
            f"{status_icon} {doc_name}: {doc_stats['chunks']} chunks ({doc_stats['status']})"
        )

    logger.info("=" * 60)
    logger.info("🎉 Knowledge Base Seeding Complete!")
    logger.info("=" * 60)

    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Seed knowledge base into Qdrant vector store"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset collection before seeding",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Seed only a specific file",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size in characters (default: 1000)",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=200,
        help="Overlap between chunks in characters (default: 200)",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="security_knowledge",
        help="Qdrant collection name (default: security_knowledge, also: incident_playbooks)",
    )
    parser.add_argument(
        "--directory",
        type=Path,
        help="Specific directory to seed (e.g., knowledge-base/playbooks/)",
    )
    parser.add_argument(
        "--kb-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "knowledge-base",
        help="Knowledge base directory (default: ../knowledge-base)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determinar directorio de trabajo
    if args.directory:
        # Directorio específico proporcionado
        work_dir = args.directory if args.directory.is_absolute() else args.kb_dir / args.directory
    else:
        # Usar directorio de knowledge base por defecto
        work_dir = args.kb_dir

    # Validar directorio
    if not work_dir.exists():
        logger.error(f"Directory not found: {work_dir}")
        sys.exit(1)

    # Ejecutar seeding
    try:
        stats = asyncio.run(
            seed_knowledge_base(
                knowledge_base_dir=work_dir,
                reset=args.reset,
                specific_file=args.file,
                chunk_size=args.chunk_size,
                overlap=args.overlap,
                collection_name=args.collection,
            )
        )

        # Exit code basado en resultados
        if stats["failed"] > 0:
            sys.exit(1)
        elif stats["total_documents"] == 0:
            logger.warning("No documents were processed")
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

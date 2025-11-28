from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import hashlib


class VectorService:
    """Service for vector embeddings and similarity search"""

    def __init__(self):
        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))

        # Initialize embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_or_create_collection(self, user_id: int, kb_id: int):
        """Get or create a collection for a knowledge base"""
        collection_name = f"user_{user_id}_kb_{kb_id}"
        return self.client.get_or_create_collection(name=collection_name)

    def add_documents(
        self,
        user_id: int,
        kb_id: int,
        document_id: int,
        chunks: List[str],
        metadata: List[Dict[str, Any]] = None
    ) -> List[str]:
        """Add document chunks to vector store"""
        collection = self.get_or_create_collection(user_id, kb_id)

        # Generate embeddings
        embeddings = self.model.encode(chunks).tolist()

        # Generate IDs
        ids = [
            f"doc_{document_id}_chunk_{i}"
            for i in range(len(chunks))
        ]

        # Prepare metadata
        if metadata is None:
            metadata = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
        else:
            for i, meta in enumerate(metadata):
                meta.update({"document_id": document_id, "chunk_index": i})

        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadata,
            ids=ids
        )

        return ids

    def search(
        self,
        user_id: int,
        kb_id: int,
        query: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Search for similar chunks"""
        try:
            collection = self.get_or_create_collection(user_id, kb_id)

            # Generate query embedding
            query_embedding = self.model.encode([query]).tolist()

            # Search
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )

            return {
                "documents": results['documents'][0] if results['documents'] else [],
                "metadatas": results['metadatas'][0] if results['metadatas'] else [],
                "distances": results['distances'][0] if results['distances'] else [],
            }
        except Exception as e:
            return {
                "documents": [],
                "metadatas": [],
                "distances": [],
                "error": str(e)
            }

    def delete_document(self, user_id: int, kb_id: int, document_id: int):
        """Delete all chunks for a document"""
        try:
            collection = self.get_or_create_collection(user_id, kb_id)

            # Get all IDs for this document
            # Note: ChromaDB doesn't have a direct way to filter by metadata for deletion
            # So we'll use a workaround
            results = collection.get()
            ids_to_delete = [
                id for id, meta in zip(results['ids'], results['metadatas'])
                if meta.get('document_id') == document_id
            ]

            if ids_to_delete:
                collection.delete(ids=ids_to_delete)

        except Exception:
            pass

    def delete_knowledge_base(self, user_id: int, kb_id: int):
        """Delete entire knowledge base collection"""
        try:
            collection_name = f"user_{user_id}_kb_{kb_id}"
            self.client.delete_collection(name=collection_name)
        except Exception:
            pass


# Create singleton instance
vector_service = VectorService()

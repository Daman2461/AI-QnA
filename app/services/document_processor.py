import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    TextLoader,
    PDFMinerLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
)
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.config import settings
from app.models.models import Document, DocumentEmbedding, Question
from app.core.exceptions import DocumentProcessingError

# Map file extensions to appropriate loaders
LOADER_MAPPING = {
    ".txt": TextLoader,
    ".pdf": PDFMinerLoader,
    ".docx": Docx2txtLoader,
    ".md": UnstructuredMarkdownLoader,
}

class DocumentProcessor:
    def __init__(self, db: Session):
        self.db = db
        # Use a simple approach for embeddings since OpenAI might not be available
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        # Initialize FAISS and HuggingFaceEmbeddings for local vector search
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

    def process_document(self, document: Document) -> None:
        """Process a document and store its embeddings."""
        print("process_document called for document:", document.id)
        try:
            # Update document status
            document.processing_status = "processing"
            self.db.commit()

            # Load document content
            file_extension = os.path.splitext(document.file_path)[1].lower()
            if file_extension not in LOADER_MAPPING:
                raise DocumentProcessingError(
                    f"Unsupported file type: {file_extension}"
                )

            loader = LOADER_MAPPING[file_extension](document.file_path)
            documents = loader.load()

            # Split text into chunks
            chunks = self.text_splitter.split_documents(documents)

            # Prepare Pinecone records for raw text ingestion
            for i, chunk in enumerate(chunks):
                # Store chunk in database and generate embedding
                embedding = self.embeddings.embed_documents([chunk.page_content])[0]
                doc_embedding = DocumentEmbedding(
                    document_id=document.id,
                    chunk_index=i,
                    chunk_text=chunk.page_content,
                    embedding=embedding
                )
                self.db.add(doc_embedding)
                print(f"Stored embedding: doc_id={document.id}, chunk_index={i}")

            # Update document status
            document.processing_status = "completed"
            document.processed_at = datetime.utcnow()
            self.db.commit()

        except Exception as e:
            print("UPLOAD ERROR:", e)
            traceback.print_exc()  # Print the full traceback
            # Only try to remove file if file_path is defined and exists
            try:
                if 'file_path' in locals() and os.path.exists(document.file_path):
                    os.remove(document.file_path)
            except Exception as cleanup_error:
                print("Cleanup error:", cleanup_error)
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    def get_relevant_chunks(
        self, document_id: int, query: str, k: int = 3
    ) -> List[Dict[str, Any]]:
        """Get the most relevant chunks for a query using simple text matching."""
        # Get all chunks for the document
        chunks = self.db.query(DocumentEmbedding).filter(
            DocumentEmbedding.document_id == document_id
        ).all()

        if not chunks:
            return []

        # Simple relevance scoring based on word overlap
        scored_chunks = []
        query_words = set(query.lower().split())
        
        for chunk in chunks:
            chunk_words = set(chunk.chunk_text.lower().split())
            overlap = len(query_words.intersection(chunk_words))
            scored_chunks.append((overlap, chunk))
        
        # Sort by relevance score and return top k
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        return [
            {
                "text": chunk.chunk_text,
                "chunk_index": chunk.chunk_index,
                "relevance_score": score
            }
            for score, chunk in scored_chunks[:k]
        ]

    def get_document_summary(self, document_id: int) -> str:
        """Generate a simple summary of the document."""
        # Get all chunks for the document
        chunks = self.db.query(DocumentEmbedding).filter(
            DocumentEmbedding.document_id == document_id
        ).order_by(DocumentEmbedding.chunk_index).all()

        if not chunks:
            return ""

        # Combine chunks into a single text
        full_text = "\n".join(chunk.chunk_text for chunk in chunks)

        # Simple summary: first 500 characters + "..."
        if len(full_text) > 500:
            summary = full_text[:500] + "..."
        else:
            summary = full_text

        return summary

    def process_question(self, question: Question, db: Session) -> None:
        try:
            # Update question status
            question.processing_status = "processing"
            db.commit()

            # Load document content
            file_extension = os.path.splitext(question.file_path)[1].lower()
            if file_extension not in LOADER_MAPPING:
                raise DocumentProcessingError(
                    f"Unsupported file type: {file_extension}"
                )

            loader = LOADER_MAPPING[file_extension](question.file_path)
            documents = loader.load()

            # Split text into chunks
            chunks = self.text_splitter.split_documents(documents)

            # Store chunks without embeddings for now (simplified approach)
            for i, chunk in enumerate(chunks):
                # Store chunk in database without embedding
                doc_embedding = DocumentEmbedding(
                    document_id=question.document_id,
                    chunk_index=i,
                    chunk_text=chunk.page_content,
                    embedding=[]  # Empty list for now
                )
                db.add(doc_embedding)

            # Update question status
            question.processing_status = "completed"
            question.processed_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            print("QUESTION ERROR:", e)  # Add this line
            db.delete(question)
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=str(e)
            ) 
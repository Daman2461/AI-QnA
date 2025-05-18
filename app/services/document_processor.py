import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import (
    TextLoader,
    PDFMinerLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Document, DocumentEmbedding
from app.core.exceptions import DocumentProcessingError
from app.services.qa_service import get_qa_chain

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
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL_NAME
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def process_document(self, document: Document) -> None:
        """Process a document and store its embeddings."""
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

            # Create embeddings for each chunk
            for i, chunk in enumerate(chunks):
                # Get embedding for the chunk
                embedding = self.embeddings.embed_query(chunk.page_content)

                # Store embedding in database
                doc_embedding = DocumentEmbedding(
                    document_id=document.id,
                    chunk_index=i,
                    chunk_text=chunk.page_content,
                    embedding=embedding
                )
                self.db.add(doc_embedding)

            # Update document status
            document.processing_status = "completed"
            document.processed_at = datetime.utcnow()
            self.db.commit()

        except Exception as e:
            document.processing_status = "failed"
            self.db.commit()
            raise DocumentProcessingError(f"Error processing document: {str(e)}")

    def get_relevant_chunks(
        self, document_id: int, query: str, k: int = 3
    ) -> List[Dict[str, Any]]:
        """Get the most relevant chunks for a query."""
        # Get all embeddings for the document
        embeddings = self.db.query(DocumentEmbedding).filter(
            DocumentEmbedding.document_id == document_id
        ).all()

        if not embeddings:
            return []

        # Create FAISS index
        texts = [e.chunk_text for e in embeddings]
        vectors = [e.embedding for e in embeddings]
        vectorstore = FAISS.from_embeddings(
            text_embeddings=list(zip(texts, vectors)),
            embedding=self.embeddings,
            metadatas=[{"chunk_index": i} for i in range(len(texts))]
        )

        # Search for relevant chunks
        docs = vectorstore.similarity_search(query, k=k)
        return [
            {
                "text": doc.page_content,
                "chunk_index": doc.metadata["chunk_index"]
            }
            for doc in docs
        ]

    def get_document_summary(self, document_id: int) -> str:
        """Generate a summary of the document using LangChain."""
        # Get all chunks for the document
        chunks = self.db.query(DocumentEmbedding).filter(
            DocumentEmbedding.document_id == document_id
        ).order_by(DocumentEmbedding.chunk_index).all()

        if not chunks:
            return ""

        # Combine chunks into a single text
        full_text = "\n".join(chunk.chunk_text for chunk in chunks)

        # Use QA chain to generate summary
        qa_chain = get_qa_chain()
        summary = qa_chain.run(
            f"Please provide a concise summary of the following text:\n\n{full_text}"
        )

        return summary 
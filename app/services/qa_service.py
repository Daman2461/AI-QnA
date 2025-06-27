from typing import Dict, Any, Optional
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain_mistralai import ChatMistralAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from sqlalchemy.orm import Session
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import BaseRetriever, Document
from pydantic import Field

from app.core.config import settings
from app.services.document_processor import DocumentProcessor
from app.core.exceptions import OpenAIError

# Custom prompt template for better Q&A
QA_PROMPT = PromptTemplate(
    template="""You are an AI assistant that helps answer questions about documents. 
    Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    
    Context:
    {context}
    
    Chat History:
    {chat_history}
    
    Human: {question}
    AI Assistant:""",
    input_variables=["context", "chat_history", "question"]
)

def get_qa_chain(llm) -> LLMChain:
    """Create a custom QA chain using LangChain and Mistral."""
    return LLMChain(
        llm=llm,
        prompt=QA_PROMPT,
        verbose=True
    )

class PineconeTextRetriever(BaseRetriever):
    index: any = Field(default=None, exclude=True)

    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'index', index)

    def get_relevant_documents(self, query, top_k=3):
        response = self.index.query(
            namespace="__default__",
            top_k=top_k,
            include_metadata=True,
            text=query
        )
        matches = response["matches"]
        # Return as LangChain Document objects
        return [Document(page_content=match["record"]["text"], metadata=match["record"].get("metadata", {})) for match in matches]

class QAService:
    def __init__(self, db: Session, document_id: int):
        self.db = db
        self.document_processor = DocumentProcessor(db)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
        from app.models.models import DocumentEmbedding
        chunks = db.query(DocumentEmbedding).filter(DocumentEmbedding.document_id == document_id).all()
        texts = [chunk.chunk_text for chunk in chunks]
        metadatas = [{"document_id": chunk.document_id, "chunk_index": chunk.chunk_index} for chunk in chunks]
        self.vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
        retriever = self.vectorstore.as_retriever()
        self.retriever = retriever
        llm = ChatMistralAI(
            mistral_api_key=settings.MISTRAL_API_KEY,
            model=settings.MISTRAL_MODEL_NAME,
            temperature=0.7
        )
        self.qa_chain = get_qa_chain(llm)

    def answer_question(
        self,
        question: str,
        chat_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Answer a question about a specific document using the real Mistral LLM.
        """
        try:
            # Get relevant chunks for the question using FAISS retriever (invoke method)
            relevant_docs = self.retriever.invoke(question)
            print("Relevant docs:", relevant_docs)
            for doc in relevant_docs:
                print("Doc metadata:", doc.metadata)
            relevant_chunks = [doc.page_content for doc in relevant_docs]

            if not relevant_chunks:
                # Fallback: return top chunks anyway, with a warning
                fallback_chunks = [doc.page_content for doc in relevant_docs]
                return {
                    "answer": "I couldn't find any relevant information in the document to answer your question. Here are the most relevant chunks found (possibly from other documents):\n\n" + "\n\n".join(fallback_chunks),
                    "confidence_score": 0,
                    "sources": [
                        {"text": chunk.page_content, "chunk_index": i, "metadata": getattr(chunk, 'metadata', {})}
                        for i, chunk in enumerate(relevant_docs)
                    ]
                }

            # Combine chunks into context
            context = "\n\n".join(relevant_chunks)

            # Get answer from QA chain (this calls Mistral via LangChain)
            result = self.qa_chain({
                "question": question,
                "chat_history": "\n".join(chat_history) if chat_history else "",
                "context": context
            })

            # Calculate confidence score (simple heuristic)
            confidence_score = min(100, int(len(relevant_chunks) * 25))

            return {
                "answer": result["text"] if "text" in result else result,
                "confidence_score": confidence_score,
                "sources": [
                    {"text": chunk, "chunk_index": i} for i, chunk in enumerate(relevant_chunks)
                ]
            }

        except Exception as e:
            # If there is an error, raise it so you see the real error in your logs
            raise RuntimeError(f"Error answering question with Mistral: {str(e)}")

    def get_conversation_history(self, question_id: int) -> list:
        """Get conversation history for a specific question."""
        # This could be expanded to store and retrieve actual conversation history
        # For now, we'll return an empty list
        return [] 
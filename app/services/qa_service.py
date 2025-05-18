from typing import Dict, Any, Optional
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import MistralChat
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.document_processor import DocumentProcessor
from app.core.exceptions import OpenAIError

# Custom prompt template for better Q&A
QA_PROMPT = PromptTemplate(
    template="""You are an AI assistant that helps answer questions about documents. 
    Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    
    Context: {context}
    
    Chat History:
    {chat_history}
    
    Human: {question}
    AI Assistant:""",
    input_variables=["context", "chat_history", "question"]
)

def get_qa_chain() -> ConversationalRetrievalChain:
    """Create a QA chain using LangChain and OpenAI."""
    try:
        # Initialize the language model (using Mistral)
        llm = MistralChat(
            mistral_api_key=settings.MISTRAL_API_KEY,
            model_name=settings.MISTRAL_MODEL_NAME,
            temperature=0.7
        )

        # Initialize memory for conversation history
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Create the QA chain
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT},
            return_source_documents=True,
            verbose=True
        )

        return qa_chain

    except Exception as e:
        raise OpenAIError(f"Error initializing QA chain (Mistral): {str(e)}")

class QAService:
    def __init__(self, db: Session):
        self.db = db
        self.document_processor = DocumentProcessor(db)
        self.qa_chain = get_qa_chain()

    def answer_question(
        self,
        document_id: int,
        question: str,
        chat_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """Answer a question about a specific document."""
        try:
            # Get relevant chunks for the question
            relevant_chunks = self.document_processor.get_relevant_chunks(
                document_id=document_id,
                query=question
            )

            if not relevant_chunks:
                return {
                    "answer": "I couldn't find any relevant information in the document to answer your question.",
                    "confidence_score": 0,
                    "sources": []
                }

            # Combine chunks into context
            context = "\n\n".join(chunk["text"] for chunk in relevant_chunks)

            # Get answer from QA chain
            result = self.qa_chain(
                {
                    "question": question,
                    "chat_history": chat_history or [],
                    "context": context
                }
            )

            # Calculate confidence score (this is a simple heuristic)
            confidence_score = min(100, int(len(relevant_chunks) * 25))

            return {
                "answer": result["answer"],
                "confidence_score": confidence_score,
                "sources": [
                    {
                        "text": chunk["text"],
                        "chunk_index": chunk["chunk_index"]
                    }
                    for chunk in relevant_chunks
                ]
            }

        except Exception as e:
            raise OpenAIError(f"Error answering question: {str(e)}")

    def get_conversation_history(self, question_id: int) -> list:
        """Get conversation history for a specific question."""
        # This could be expanded to store and retrieve actual conversation history
        # For now, we'll return an empty list
        return [] 
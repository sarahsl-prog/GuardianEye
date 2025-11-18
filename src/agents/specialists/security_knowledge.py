"""Security Knowledge Agent with RAG capabilities."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.agents.base.base_agent import BaseAgent, AgentInput, AgentOutput
from src.core.prompts import SECURITY_KNOWLEDGE_PROMPT


class SecurityKnowledgeAgent(BaseAgent):
    """Agent for answering security questions with RAG-enhanced knowledge."""

    def __init__(self, llm, vector_store=None):
        """Initialize the Security Knowledge Agent.

        Args:
            llm: Language model instance
            vector_store: Optional vector store for RAG
        """
        super().__init__(llm, name="security_knowledge")
        self.vector_store = vector_store
        self.retriever = vector_store.as_retriever() if vector_store else None

    def get_prompt_template(self) -> str:
        """Return the prompt template for this agent."""
        return SECURITY_KNOWLEDGE_PROMPT

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process security knowledge query with optional RAG."""
        question = input_data.query

        # If we have a retriever, use RAG
        context_docs = []
        if self.retriever:
            try:
                # Retrieve relevant documents
                context_docs = await self.retriever.ainvoke(question)
                context_text = "\n\n".join([doc.page_content for doc in context_docs[:3]])

                # Enhanced prompt with context
                rag_prompt = f"""Use the following context to help answer the question:

Context:
{context_text}

{SECURITY_KNOWLEDGE_PROMPT}
"""
                prompt = ChatPromptTemplate.from_template(rag_prompt)
            except Exception as e:
                # Fall back to basic prompt if RAG fails
                prompt = ChatPromptTemplate.from_template(self.get_prompt_template())
        else:
            prompt = ChatPromptTemplate.from_template(self.get_prompt_template())

        chain = prompt | self.llm | StrOutputParser()
        response = await chain.ainvoke({"question": question})

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "model": getattr(self.llm, "model_name", "unknown"),
                "rag_enabled": self.retriever is not None,
                "docs_retrieved": len(context_docs)
            }
        )

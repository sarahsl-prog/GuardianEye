"""Security Knowledge Agent for answering security questions."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.base.base_agent import AgentInput, AgentOutput, BaseAgent
from src.core.prompts import SECURITY_KNOWLEDGE_PROMPT


class SecurityKnowledgeAgent(BaseAgent):
    """Agent for answering security architecture and best practices questions."""

    def __init__(self, llm):
        """Initialize security knowledge agent."""
        super().__init__(llm, name="security_knowledge")
        self.parser = StrOutputParser()

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for security knowledge."""
        return ChatPromptTemplate.from_messages([
            ("system", SECURITY_KNOWLEDGE_PROMPT),
            ("user", """Question: {question}
            Context: {context}

            Please provide a comprehensive answer based on security best practices.""")
        ])

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Process security knowledge request.

        Args:
            input_data: Security question

        Returns:
            AgentOutput with answer
        """
        # Create chain
        chain = self.get_prompt_template() | self.llm | self.parser

        # Prepare input
        question = input_data.query
        context = input_data.context.get("knowledge_context", "General security inquiry")

        # Execute
        response = await chain.ainvoke({
            "question": question,
            "context": context
        })

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "question_type": "security_knowledge",
            }
        )

"""Compliance Auditor Agent for security compliance reviews."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.agents.base.base_agent import BaseAgent, AgentInput, AgentOutput
from src.core.prompts import COMPLIANCE_AUDITOR_PROMPT


class ComplianceAuditorAgent(BaseAgent):
    """Agent for reviewing compliance findings and assessments."""

    def __init__(self, llm):
        """Initialize the Compliance Auditor Agent."""
        super().__init__(llm, name="compliance_auditor")

    def get_prompt_template(self) -> str:
        """Return the prompt template for this agent."""
        return COMPLIANCE_AUDITOR_PROMPT

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process compliance audit request."""
        framework = input_data.context.get("framework", "NIST CSF")
        findings = input_data.context.get("findings", input_data.query)

        prompt = ChatPromptTemplate.from_template(self.get_prompt_template())
        chain = prompt | self.llm | StrOutputParser()

        response = await chain.ainvoke({
            "framework": framework,
            "findings": findings
        })

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "model": getattr(self.llm, "model_name", "unknown"),
                "framework": framework
            }
        )

"""Compliance Auditor Agent for compliance assessment and reporting."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.base.base_agent import AgentInput, AgentOutput, BaseAgent
from src.core.prompts import COMPLIANCE_AUDITOR_PROMPT


class ComplianceAuditorAgent(BaseAgent):
    """Agent for analyzing compliance findings and generating reports."""

    def __init__(self, llm):
        """Initialize compliance auditor agent."""
        super().__init__(llm, name="compliance_auditor")
        self.parser = StrOutputParser()

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for compliance auditing."""
        return ChatPromptTemplate.from_messages([
            ("system", COMPLIANCE_AUDITOR_PROMPT),
            ("user", """Compliance Findings: {findings}
            Framework: {framework}
            Scope: {scope}

            Please analyze these compliance findings and provide your assessment.""")
        ])

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Process compliance audit request.

        Args:
            input_data: Compliance findings

        Returns:
            AgentOutput with audit results
        """
        # Create chain
        chain = self.get_prompt_template() | self.llm | self.parser

        # Prepare input
        findings = input_data.context.get("findings", input_data.query)
        framework = input_data.context.get("framework", "General security best practices")
        scope = input_data.context.get("scope", "Organization-wide")

        # Execute
        response = await chain.ainvoke({
            "findings": findings,
            "framework": framework,
            "scope": scope
        })

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "framework": framework,
                "scope": scope,
            }
        )

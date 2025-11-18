"""Anomaly Investigation Agent for analyzing anomalies in logs and behavior."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.base.base_agent import AgentInput, AgentOutput, BaseAgent
from src.core.prompts import ANOMALY_INVESTIGATION_PROMPT


class AnomalyInvestigationAgent(BaseAgent):
    """Agent for investigating anomalies in security logs and behavior."""

    def __init__(self, llm):
        """Initialize anomaly investigation agent."""
        super().__init__(llm, name="anomaly_investigation")
        self.parser = StrOutputParser()

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for anomaly investigation."""
        return ChatPromptTemplate.from_messages([
            ("system", ANOMALY_INVESTIGATION_PROMPT),
            ("user", """Anomaly Data: {anomaly_data}
            Baseline: {baseline}

            Please investigate this anomaly and provide your analysis.""")
        ])

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Process anomaly investigation request.

        Args:
            input_data: Anomaly details

        Returns:
            AgentOutput with investigation results
        """
        # Create chain
        chain = self.get_prompt_template() | self.llm | self.parser

        # Prepare input
        anomaly_data = input_data.context.get("anomaly_data", input_data.query)
        baseline = input_data.context.get("baseline", "Normal behavior not specified")

        # Execute
        response = await chain.ainvoke({
            "anomaly_data": anomaly_data,
            "baseline": baseline
        })

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "has_baseline": "baseline" in input_data.context,
            }
        )

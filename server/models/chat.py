from enum import StrEnum

from pydantic import BaseModel


class ChatModel(StrEnum):
    GPT_6_ASTRA = "gpt-6-astra"
    GPT_6_1_SOL = "gpt-6.1-sol"
    GPT_6_SOL = "gpt-6-sol"
    GPT_6_LUNA = "gpt-6-luna"
    GPT_5_6_SOL = "gpt-5.6-sol"
    GPT_5_6_TERRA = "gpt-5.6-terra"
    GPT_5_6_LUNA = "gpt-5.6-luna"


class ModelOption(BaseModel):
    id: ChatModel
    name: str
    description: str
    is_default: bool = False


MODEL_OPTIONS = (
    ModelOption(
        id=ChatModel.GPT_6_ASTRA,
        name="GPT-6 Astra",
        description="Most capable GPT-6 model for demanding reasoning and coding.",
    ),
    ModelOption(
        id=ChatModel.GPT_6_1_SOL,
        name="GPT-6.1 Sol",
        description="Newer Sol model balancing intelligence and cost.",
    ),
    ModelOption(
        id=ChatModel.GPT_6_SOL,
        name="GPT-6 Sol",
        description="GPT-6 model for complex coding and agentic workflows.",
    ),
    ModelOption(
        id=ChatModel.GPT_6_LUNA,
        name="GPT-6 Luna",
        description="Efficient GPT-6 model for focused, high-volume tasks.",
    ),
    ModelOption(
        id=ChatModel.GPT_5_6_SOL,
        name="GPT-5.6 Sol",
        description="Highest-capability GPT-5.6 model for complex work.",
    ),
    ModelOption(
        id=ChatModel.GPT_5_6_TERRA,
        name="GPT-5.6 Terra",
        description="Balances intelligence, latency, and cost.",
    ),
    ModelOption(
        id=ChatModel.GPT_5_6_LUNA,
        name="GPT-5.6 Luna",
        description="Efficient GPT-5.6 model for cost-sensitive workloads.",
        is_default=True,
    ),
)

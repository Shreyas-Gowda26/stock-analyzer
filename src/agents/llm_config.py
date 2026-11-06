
import os

from dotenv import load_dotenv
from crewai import LLM


# Load environment variables from project root
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY is missing. "
        "Please configure it in your .env file."
    )


llm = LLM(
    model="openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    temperature=0.2,
    max_tokens=2000
)

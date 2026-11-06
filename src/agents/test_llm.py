
from src.agents.llm_config import llm

response = llm.call(
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: OpenRouter connection successful."
        }
    ]
)

print("LLM Response:")
print(response)

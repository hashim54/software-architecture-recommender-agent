import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))
from intake_agent import IntakeAgent

def test_intake_agent():
    user_query = (
        "I need an architecture for a batch ingestion use case. "
        "The process must run daily, ingest CSV files into a cloud data lake, "
        "and be able to scale. Cost efficiency is important."
    )
    conversation_history = []
    agent = IntakeAgent()
    input_data = {
        "user_query": user_query,
        "conversation_history": conversation_history
    }
    context = {}
    result = agent.execute(input_data, context)
    print("=== Recommendation ===")
    print(result["recommendation"])
    print("\n=== URLs ===")
    for url in result["urls"]:
        print(url)
    print("\n=== Updated Conversation History ===")
    for entry in result["conversation_history"]:
        print(entry)

if __name__ == "__main__":
    test_intake_agent()

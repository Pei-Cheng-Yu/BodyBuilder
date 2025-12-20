import asyncio
import sys
from pathlib import Path

# Fix path
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent
sys.path.append(str(backend_dir))
if current_file:
    from app.graph.llm.ollama import get_ollama_gpt_20


async def test_ncku_connection():
    print("🧪 Testing NCKU Ollama Authentication...")

    model = get_ollama_gpt_20()
    test_prompt = "Say 'NCKU Connection Verified'"

    try:
        print("📡 Sending Async Request...")
        # We test ainvoke specifically since that's what LangGraph uses
        resp = await model.ainvoke(test_prompt)
        print(f"✅ Success! Response: {resp.content}")

    except Exception as e:
        print("\n❌ Connection Failed!")
        print(f"Error: {str(e)}")
        if "401" in str(e):
            print(
                "🔑 Hint: Check if NCKU_API_KEY in your .env is correct and not expired."
            )


if __name__ == "__main__":
    asyncio.run(test_ncku_connection())

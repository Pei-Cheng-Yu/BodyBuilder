import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

host = os.getenv("NCKU_HOST")
api_key = os.getenv("NCKU_API_KEY")


def get_ollama():
    """
    Creates a LangChain ChatModel connected to NCKU's authenticated Ollama server.
    """
    print(f"📡 Connecting to NCKU Gateway: {host}...")

    return ChatOllama(
        model="gemma3:4b",
        base_url=host,
        temperature=0,
        # ✅ Standard headers
        headers={"Authorization": f"Bearer {api_key}"},
        # ✅ Explicitly force headers into the HTTP client
        client_kwargs={"headers": {"Authorization": f"Bearer {api_key}"}},
    )


def get_ollama_gpt_120():
    """
    Creates a LangChain ChatModel connected to NCKU's authenticated Ollama server.
    """
    print(f"📡 Connecting to NCKU Gateway: {host}...")

    return ChatOllama(
        model="gpt-oss:120b",
        base_url=host,
        temperature=0,
        # ✅ Standard headers
        max_retries=3,
        headers={"Authorization": f"Bearer {api_key}"},
        # ✅ Explicitly force headers into the HTTP client
        client_kwargs={"headers": {"Authorization": f"Bearer {api_key}"}},
    )


def get_ollama_gpt_20():
    """
    Creates a LangChain ChatModel connected to NCKU's authenticated Ollama server.
    """
    print(f"📡 Connecting to NCKU Gateway: {host}...")

    return ChatOllama(
        model="gpt-oss:20b",
        base_url=host,
        temperature=0,
        # ✅ Standard headers
        max_retries=3,
        headers={"Authorization": f"Bearer {api_key}"},
        # ✅ Explicitly force headers into the HTTP client
        client_kwargs={"headers": {"Authorization": f"Bearer {api_key}"}},
    )

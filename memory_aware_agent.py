import os
from mem0 import Memory
from openai import OpenAI


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

QUADRANT_HOST = "localhost"

NEO4J_URL="bolt://localhost:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="password"

USER_ID = "ak_001" 


config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "text-embedding-3-large"},
    },
    "llm": {"provider": "openai", "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4.1"}},
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QUADRANT_HOST,
            "port": 6333,
        },
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {"url": NEO4J_URL, "username": NEO4J_USERNAME, "password": NEO4J_PASSWORD},
    },
}

mem_client = Memory.from_config(config)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


messages = []

def chat(message):
    mem_result = mem_client.search(query=message, user_id=USER_ID)
    memories = "\n".join([m["memory"] for m in mem_result.get("results")])

    SYSTEM_PROMPT = f"""
    You are a Memory-Aware Agent.
    
    - You have access to previous user memories listed below.
    - When answering the user's new message, you MUST use relevant memories if they exist.
    - If no relevant memory matches, reason and answer normally.
    - Always be factually accurate and avoid guessing beyond available memories.

    MEMORY CONTEXT:
    {memories}
    """

    chat_messages = [
        { "role": "system", "content": SYSTEM_PROMPT },
        { "role": "user", "content": message }
    ]

    result = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=chat_messages
    )

    assistant_reply = result.choices[0].message.content

    print("Saving memory!")
    mem_client.add(
        [{"role": "user", "content": message}, {"role": "assistant", "content": assistant_reply}],
            user_id=USER_ID
    )

    print("Assistant says", assistant_reply)    

    while True:
        message = input(">> ")
        print("BOT: ", chat(message=message))

def is_new_fact(new_text, old_memories):
    return new_text.strip() not in old_memories.strip()

chat("Hello!!")

import os
from mem0 import Memory
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QUADRANT_HOST = os.getenv("QUADRANT_HOST")
NEO4J_URL= os.getenv("NEO4J_URL")
NEO4J_USERNAME= os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD= os.getenv("NEO4J_PASSWORD")

USER_ID = "ak007"

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "text-embedding-3-small"},
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

def search_memories(message):
    results = mem_client.search(message, user_id= USER_ID) 
    memories_list = [
        r.get('memory', '') 
        for r in results.get('results', []) 
        if r.get('memory') and r.get('score', 0) > 0.2
    ]
    memories_text = "\n".join(memories_list)
    return memories_text

def chat(message):
    memories = search_memories(message)

    SYSTEM_PROMPT =  f"""
    You are a memory aware Agent designed to analyse input content, extract structured information and maintain a memory store. 

    Rules: 
    Your tone should be professional, precise and clear
    You should use the memories that I have saved in {memories}
    """
    messages = [
        { "role": "system", "content": SYSTEM_PROMPT },
        { "role": "user", "content": message }
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=messages
    )

    messages.append(
        { "role": "assistant", "content": response.choices[0].message.content }
    )

    mem_client.add(messages, user_id =USER_ID)

    return response

def main():
    print("Assistant Ready! (type 'exit' to quit)\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        response = chat(user_input)
        response_content = response.choices[0].message.content

        print(f"Assistant: {response_content}\n")

if __name__ == "__main__":
    main()

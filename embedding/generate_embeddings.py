from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

# Create embeddings
response = client.embeddings.create(
    model="sentence-transformers/all-mpnet-base-v2",
    input="Run an embedding model with MAX Serve!",
)

print(f"{response.data[0].embedding[:5]}")

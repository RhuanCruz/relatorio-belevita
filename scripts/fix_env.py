
import os

env_content = """
AZURE_ENDPOINT_MODEL=https://opus-brain-resource.cognitiveservices.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15
AZURE_API_KEY=C7EH1RlzHU4D76PGn0j4XlBsDdW3vTAjGVXpOPrXErEcdAWnWErnJQQJ99BLACZoyfiXJ3w3AAAAACOGYPNJ
MODEL_NAME=text-embedding-ada-002
MODEL_VERSION=2023-05-15
"""

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

print(f"Appending to {env_path}")

try:
    with open(env_path, 'a') as f:
        f.write(env_content)
    print("Successfully appended credentials.")
except Exception as e:
    print(f"Error writing .env: {e}")

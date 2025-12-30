
import os

env_content = """
PINECONE_API_KEY=pcsk_36K9qG_KisYZPn9dnZJL6T6j1rkL3cX8BU7CbBiNtToeBKEg9yCjk66YVHHZBkBoBH6e5r
"""

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

print(f"Appending to {env_path}")

try:
    with open(env_path, 'a') as f:
        f.write(env_content)
    print("Successfully appended PINECONE_API_KEY.")
except Exception as e:
    print(f"Error writing .env: {e}")

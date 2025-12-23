
import os
from dotenv import load_dotenv

load_dotenv(override=True)

key = os.getenv("AZURE_API_KEY")
if key:
    print(f"Key loaded: {key[:5]}...{key[-5:]} (Length: {len(key)})")
else:
    print("No AZURE_API_KEY found")

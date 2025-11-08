from dotenv import load_dotenv

load_dotenv()
import os
import secrets
import uvicorn
from app import create_app


# Generate API key if not found in environment
if not os.getenv("API_KEY"):
    generated_key = secrets.token_urlsafe(32)
    os.environ["API_KEY"] = generated_key
    print("="*60)
    print("⚠️  No API_KEY found in environment!")
    print("🔑 Generated API Key:")
    print(f"   {generated_key}")
    print("")
    print("💡 To persist this key, add it to your .env file:")
    print(f"   API_KEY={generated_key}")
    print("="*60)
    print()

app = create_app()
port = int(os.getenv("PORT", 7777))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

import os
from dotenv import load_dotenv

load_dotenv()

hf_token = os.getenv("HF_TOKEN")

if not hf_token:
    print("❌ HF_TOKEN not found in .env")
    exit(1)

print(f"✅ HF_TOKEN found: {hf_token[:10]}...")

try:
    from pyannote.audio import Pipeline
    print("✅ Pyannote imported successfully")
    
    print("\n🔄 Attempting to load model...")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    print("✅ Model loaded successfully!")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    print("\nMake sure you:")
    print("1. Have a valid HF token in .env")
    print("2. Accepted the license at: https://huggingface.co/pyannote/speaker-diarization-3.1")
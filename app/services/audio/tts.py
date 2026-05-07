import edge_tts
import uuid
import os

# Microsoft's explicit Arabic Neural Voices
VOICE = "ar-SA-HamedNeural"  # Professional male Saudi voice

async def generate_speech(text: str) -> str:
    """
    Converts Synthesized Arabic Text into an MP3 Audio file for playback to the user.
    """
    os.makedirs("output_audio", exist_ok=True)
    filename = f"output_audio/{uuid.uuid4().hex}.mp3"
    
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)
    
    return filename

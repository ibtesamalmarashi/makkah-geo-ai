import io
import asyncio
from faster_whisper import WhisperModel

# Initialize lightweight model for fast local transcription
model = WhisperModel("tiny", device="cpu", compute_type="int8")

async def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribes raw PCM/WAV audio bytes into Arabic text offline.
    """
    def _transcribe():
        segments, _ = model.transcribe(io.BytesIO(audio_bytes), language="ar")
        return " ".join([segment.text for segment in segments])
        
    text = await asyncio.to_thread(_transcribe)
    return text.strip()

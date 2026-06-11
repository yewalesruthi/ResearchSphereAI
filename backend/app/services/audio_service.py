import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import whisper
except ImportError:
    whisper = None  # type: ignore

from pydub import AudioSegment

from app.utils.config import get_settings

logger = logging.getLogger(__name__)

_whisper_model = None


def get_whisper_model():
    global _whisper_model
    if whisper is None:
        raise RuntimeError(
            "openai-whisper is not installed. Run: pip install openai-whisper"
        )
    if _whisper_model is None:
        settings = get_settings()
        logger.info("Loading Whisper model: %s", settings.whisper_model)
        _whisper_model = whisper.load_model(settings.whisper_model)
    return _whisper_model


def convert_to_wav(input_path: str, output_path: str) -> str:
    ext = Path(input_path).suffix.lower().lstrip(".")
    if ext == "wav":
        return input_path
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav")
    return output_path


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def transcribe_audio(file_path: str) -> Tuple[str, List[Dict[str, Any]], float]:
    settings = get_settings()
    wav_path = file_path
    temp_wav = None
    if not file_path.lower().endswith(".wav"):
        temp_wav = str(Path(file_path).with_suffix(".converted.wav"))
        wav_path = convert_to_wav(file_path, temp_wav)

    model = get_whisper_model()
    result = model.transcribe(wav_path)

    segments = []
    for seg in result.get("segments", []):
        segments.append(
            {
                "start": seg["start"],
                "end": seg["end"],
                "start_formatted": format_timestamp(seg["start"]),
                "end_formatted": format_timestamp(seg["end"]),
                "text": seg["text"].strip(),
            }
        )

    duration = segments[-1]["end"] if segments else 0.0
    transcript = result.get("text", "").strip()

    if temp_wav and Path(temp_wav).exists():
        Path(temp_wav).unlink()

    return transcript, segments, duration


def segments_to_json(segments: List[Dict[str, Any]]) -> str:
    return json.dumps(segments)

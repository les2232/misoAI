import shutil
import subprocess


def get_voice_engine():
    """Return the available text-to-speech engine, if one exists."""
    return shutil.which("espeak-ng") or shutil.which("espeak")


def voice_available():
    return get_voice_engine() is not None


def speak(text):
    """Speak text out loud if a local TTS engine is available."""
    text = text.strip()

    if not text:
        return False, "I need something to say."

    engine = get_voice_engine()

    if engine is None:
        return (
            False,
            "Voice output is not installed yet. Try: sudo apt install espeak-ng",
        )

    subprocess.run([engine, text], check=False)
    return True, text


def print_voice_status():
    engine = get_voice_engine()

    print()
    print("Miso voice status:")

    if engine is None:
        print("  Voice engine: not installed")
        print("  Install with: sudo apt install espeak-ng")
    else:
        print(f"  Voice engine: {engine}")
        print("  Status: ready")

    print()

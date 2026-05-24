import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATH = PROJECT_ROOT / "data" / "memory.json"


def _normalize_key(key):
    return key.strip().lower().replace(" ", "_")


def _ensure_memory_file():
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not MEMORY_PATH.exists():
        MEMORY_PATH.write_text("{}", encoding="utf-8")


def load_memories():
    _ensure_memory_file()

    try:
        return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_memories(memories):
    MEMORY_PATH.write_text(
        json.dumps(memories, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def remember(key, value):
    memories = load_memories()
    normalized_key = _normalize_key(key)
    memories[normalized_key] = value.strip()
    save_memories(memories)
    return normalized_key


def recall(key):
    memories = load_memories()
    normalized_key = _normalize_key(key)
    return memories.get(normalized_key)


def forget(key):
    memories = load_memories()
    normalized_key = _normalize_key(key)

    if normalized_key in memories:
        del memories[normalized_key]
        save_memories(memories)
        return True

    return False


def list_memories():
    return load_memories()

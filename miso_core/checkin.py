import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHECKIN_PATH = PROJECT_ROOT / "data" / "checkins.jsonl"


def _now_local_iso():
    return datetime.now().isoformat(timespec="seconds")


def save_checkin(mood, goal, first_step):
    CHECKIN_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "created_at": _now_local_iso(),
        "mood": mood,
        "goal": goal,
        "first_step": first_step,
    }

    with CHECKIN_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, sort_keys=True) + "\n")

    return entry


def get_latest_checkin():
    if not CHECKIN_PATH.exists():
        return None

    lines = CHECKIN_PATH.read_text(encoding="utf-8").splitlines()

    for line in reversed(lines):
        if not line.strip():
            continue

        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue

    return None


def print_latest_checkin():
    entry = get_latest_checkin()

    if entry is None:
        print("I do not have any check-ins saved yet.")
        return

    print()
    print("Latest check-in:")
    print(f"  Time: {entry.get('created_at', 'unknown')}")
    print(f"  Feeling: {entry.get('mood', '')}")
    print(f"  Goal: {entry.get('goal', '')}")
    print(f"  Tiny first step: {entry.get('first_step', '')}")
    print()


def run_checkin():
    print()
    print("Daily check-in")
    print("Let's make today feel a little more organized.")
    print()

    try:
        mood = input("How are you feeling today? ").strip()
        goal = input("What is one thing you want to finish? ").strip()
        first_step = input("What is one tiny first step? ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Check-in canceled.")
        return

    mood = mood or "not sure yet"
    goal = goal or "pick one important thing"
    first_step = first_step or "choose the smallest visible step"

    entry = save_checkin(mood, goal, first_step)

    print()
    print("Check-in saved.")
    print(f"Feeling: {entry['mood']}")
    print(f"Goal: {entry['goal']}")
    print(f"Tiny first step: {entry['first_step']}")
    print()
    print("Good. Keep it small and start there.")

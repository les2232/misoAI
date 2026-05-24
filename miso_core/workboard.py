import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBOARD_PATH = PROJECT_ROOT / "data" / "workboard.json"
SNAPSHOTS_PATH = PROJECT_ROOT / "data" / "snapshots.jsonl"

INACTIVE_STATUSES = {"done", "complete", "completed", "archived", "inactive"}


def _now_local_iso():
    return datetime.now().isoformat(timespec="seconds")


def _normalize_project_name(name):
    return name.strip().lower().replace(" ", "_")


def _ensure_data_dir():
    WORKBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)


def _empty_workboard():
    return {"projects": {}}


def load_workboard():
    _ensure_data_dir()

    if not WORKBOARD_PATH.exists():
        return _empty_workboard()

    try:
        data = json.loads(WORKBOARD_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_workboard()

    if not isinstance(data, dict):
        return _empty_workboard()

    projects = data.get("projects")
    if not isinstance(projects, dict):
        data["projects"] = {}

    return data


def save_workboard(workboard):
    _ensure_data_dir()
    WORKBOARD_PATH.write_text(
        json.dumps(workboard, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def find_project_key(name, workboard=None):
    if workboard is None:
        workboard = load_workboard()

    projects = workboard.get("projects", {})
    normalized = _normalize_project_name(name)

    if normalized in projects:
        return normalized

    for key, project in projects.items():
        project_name = project.get("name", "")
        if project_name.strip().lower() == name.strip().lower():
            return key

    return None


def list_active_projects():
    projects = load_workboard().get("projects", {})
    active_projects = []

    for key, project in projects.items():
        status = project.get("status", "active").strip().lower()
        if status not in INACTIVE_STATUSES:
            active_projects.append((key, project))

    return sorted(active_projects, key=lambda item: item[1].get("name", item[0]).lower())


def upsert_project(name, status, last_finished, blocker, next_step):
    workboard = load_workboard()
    key = find_project_key(name, workboard) or _normalize_project_name(name)
    existing = workboard["projects"].get(key, {})
    now = _now_local_iso()

    project = {
        "name": name.strip() or existing.get("name", key),
        "status": status.strip() or existing.get("status", "active"),
        "last_finished": last_finished.strip() or existing.get("last_finished", ""),
        "blocker": blocker.strip() or existing.get("blocker", ""),
        "next_step": next_step.strip() or existing.get("next_step", ""),
        "created_at": existing.get("created_at", now),
        "updated_at": now,
    }

    workboard["projects"][key] = project
    save_workboard(workboard)
    return key, project


def get_project(name):
    workboard = load_workboard()
    key = find_project_key(name, workboard)

    if key is None:
        return None

    return workboard["projects"].get(key)


def save_snapshot(project_name, summary, last_finished, blocker, next_step):
    _ensure_data_dir()
    entry = {
        "created_at": _now_local_iso(),
        "project": project_name.strip(),
        "summary": summary.strip(),
        "last_finished": last_finished.strip(),
        "blocker": blocker.strip(),
        "next_step": next_step.strip(),
    }

    with SNAPSHOTS_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, sort_keys=True) + "\n")

    return entry


def get_latest_snapshot():
    if not SNAPSHOTS_PATH.exists():
        return None

    lines = SNAPSHOTS_PATH.read_text(encoding="utf-8").splitlines()

    for line in reversed(lines):
        if not line.strip():
            continue

        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue

    return None


def print_recap():
    projects = list_active_projects()

    if not projects:
        print("No active projects on the workboard yet.")
        return

    print()
    print("Active projects:")
    for _, project in projects:
        print(f"  - {project.get('name', 'Unnamed project')}")
        print(f"    Status: {project.get('status', 'active')}")
        print(f"    Next step: {project.get('next_step', '') or 'not set'}")
    print()


def print_project_resume(project_name):
    project = get_project(project_name)

    if project is None:
        print(f"I do not have a project called '{project_name}' on the workboard yet.")
        return

    print()
    print(f"Resume: {project.get('name', project_name)}")
    print(f"  Status: {project.get('status', 'active')}")
    print(f"  Last finished: {project.get('last_finished', '') or 'not set'}")
    print(f"  Blocker: {project.get('blocker', '') or 'none noted'}")
    print(f"  Next step: {project.get('next_step', '') or 'not set'}")
    print()


def print_latest_snapshot():
    entry = get_latest_snapshot()

    if entry is None:
        print("I do not have any snapshots saved yet.")
        return

    print()
    print("Latest snapshot:")
    print(f"  Time: {entry.get('created_at', 'unknown')}")
    print(f"  Project: {entry.get('project', '') or 'not set'}")
    print(f"  Where you left off: {entry.get('summary', '') or 'not set'}")
    print(f"  Last finished: {entry.get('last_finished', '') or 'not set'}")
    print(f"  Blocker: {entry.get('blocker', '') or 'none noted'}")
    print(f"  Next step: {entry.get('next_step', '') or 'not set'}")
    print()


def _print_privacy_note():
    print("Keep this personal and local. Do not enter passwords, tokens, work secrets, or institutional private data.")


def _prompt_project_fields(existing=None):
    existing = existing or {}
    name_prompt = "Project name"
    if existing.get("name"):
        name_prompt += f" [{existing['name']}]"

    name = input(f"{name_prompt}: ").strip() or existing.get("name", "")
    status = input(f"Status [{existing.get('status', 'active')}]: ").strip() or existing.get("status", "active")
    last_finished = input(f"Last finished [{existing.get('last_finished', '')}]: ").strip() or existing.get("last_finished", "")
    blocker = input(f"Blocker [{existing.get('blocker', '')}]: ").strip() or existing.get("blocker", "")
    next_step = input(f"Next step [{existing.get('next_step', '')}]: ").strip() or existing.get("next_step", "")
    return name, status, last_finished, blocker, next_step


def run_add_project():
    print()
    print("Add project")
    _print_privacy_note()
    print()

    try:
        name, status, last_finished, blocker, next_step = _prompt_project_fields()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Add project canceled.")
        return

    if not name:
        print("Project not saved. A name is required.")
        return

    _, project = upsert_project(name, status, last_finished, blocker, next_step)
    print(f"Saved project: {project['name']}")


def run_update_project():
    print()
    print("Update project")
    _print_privacy_note()
    print()

    projects = list_active_projects()
    if projects:
        print("Projects:")
        for _, project in projects:
            print(f"  - {project.get('name', 'Unnamed project')}")
        print()

    try:
        project_name = input("Project to update: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Update project canceled.")
        return

    if not project_name:
        print("Update canceled. A project name is required.")
        return

    existing = get_project(project_name)
    if existing is None:
        print(f"I do not have '{project_name}' yet. Use addproject first.")
        return

    try:
        name, status, last_finished, blocker, next_step = _prompt_project_fields(existing)
    except (KeyboardInterrupt, EOFError):
        print()
        print("Update project canceled.")
        return

    _, project = upsert_project(name, status, last_finished, blocker, next_step)
    print(f"Updated project: {project['name']}")


def run_snapshot():
    print()
    print("Snapshot")
    _print_privacy_note()
    print()

    try:
        project = input("Project: ").strip()
        summary = input("Where did you leave off? ").strip()
        last_finished = input("Last thing finished: ").strip()
        blocker = input("Blocker: ").strip()
        next_step = input("Next step: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Snapshot canceled.")
        return

    entry = save_snapshot(project, summary, last_finished, blocker, next_step)
    print(f"Snapshot saved at {entry['created_at']}.")

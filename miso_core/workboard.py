import json
import os
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKBOARD_PATH = PROJECT_ROOT / "data" / "workboard.json"
DEFAULT_SNAPSHOTS_PATH = PROJECT_ROOT / "data" / "snapshots.jsonl"

INACTIVE_STATUSES = {"done", "complete", "completed", "archived", "inactive"}


def _now_local_iso():
    return datetime.now().isoformat(timespec="seconds")


def _normalize_project_name(name):
    return name.strip().lower().replace(" ", "_")


def _path_from_env(env_name, default_path):
    configured_path = os.environ.get(env_name)
    if configured_path:
        return Path(configured_path).expanduser()
    return default_path


def get_workboard_path():
    return _path_from_env("MISO_WORKBOARD_PATH", DEFAULT_WORKBOARD_PATH)


def get_snapshots_path():
    return _path_from_env("MISO_SNAPSHOTS_PATH", DEFAULT_SNAPSHOTS_PATH)


def _ensure_data_dir():
    get_workboard_path().parent.mkdir(parents=True, exist_ok=True)
    get_snapshots_path().parent.mkdir(parents=True, exist_ok=True)


def _empty_workboard():
    return {"projects": {}}


def load_workboard():
    _ensure_data_dir()

    path = get_workboard_path()
    if not path.exists():
        return _empty_workboard()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
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
    get_workboard_path().write_text(
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


def find_project_matches(name, workboard=None):
    if workboard is None:
        workboard = load_workboard()

    query = name.strip().lower()
    if not query:
        return []

    matches = []
    for key, project in workboard.get("projects", {}).items():
        project_name = project.get("name", key)
        if query in project_name.strip().lower():
            matches.append((key, project))

    return sorted(matches, key=lambda item: item[1].get("name", item[0]).lower())


def resolve_project(name, workboard=None):
    if workboard is None:
        workboard = load_workboard()

    projects = workboard.get("projects", {})
    normalized = _normalize_project_name(name)

    if normalized in projects:
        return normalized, projects[normalized], []

    for key, project in projects.items():
        project_name = project.get("name", "")
        if project_name.strip().lower() == name.strip().lower():
            return key, project, []

    matches = find_project_matches(name, workboard)
    if len(matches) == 1:
        key, project = matches[0]
        return key, project, []

    return None, None, matches


def list_active_projects():
    projects = load_workboard().get("projects", {})
    active_projects = []

    for key, project in projects.items():
        status = project.get("status", "active").strip().lower()
        if status not in INACTIVE_STATUSES:
            active_projects.append((key, project))

    return sorted(active_projects, key=lambda item: item[1].get("name", item[0]).lower())


def upsert_project(name, status, last_finished, blocker, next_step, priority=""):
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
        "priority": priority.strip() or existing.get("priority", ""),
        "created_at": existing.get("created_at", now),
        "updated_at": now,
    }

    workboard["projects"][key] = project
    save_workboard(workboard)
    return key, project


def get_project(name):
    workboard = load_workboard()
    key, project, _ = resolve_project(name, workboard)

    if key is None:
        return None

    return project


def rename_project(current_name, new_name):
    workboard = load_workboard()
    key, project, matches = resolve_project(current_name, workboard)

    if matches:
        return "ambiguous", matches

    if key is None:
        return "missing", None

    clean_new_name = new_name.strip()
    if not clean_new_name:
        return "empty", None

    new_key = _normalize_project_name(clean_new_name)
    projects = workboard["projects"]

    if new_key != key and new_key in projects:
        return "exists", projects[new_key]

    renamed_project = dict(project)
    renamed_project["name"] = clean_new_name
    renamed_project["updated_at"] = _now_local_iso()

    if new_key != key:
        del projects[key]

    projects[new_key] = renamed_project
    save_workboard(workboard)
    return "renamed", renamed_project


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

    with get_snapshots_path().open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, sort_keys=True) + "\n")

    return entry


def get_latest_snapshot(project_name=None):
    path = get_snapshots_path()
    if not path.exists():
        return None

    lines = path.read_text(encoding="utf-8").splitlines()
    normalized_project_name = None
    if project_name:
        normalized_project_name = _normalize_project_name(project_name)

    for line in reversed(lines):
        if not line.strip():
            continue

        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        if normalized_project_name is None:
            return entry

        entry_project = entry.get("project", "")
        if _normalize_project_name(entry_project) == normalized_project_name:
            return entry

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
    _, project, matches = resolve_project(project_name)

    if matches:
        print("More than one project matched. Please be more specific:")
        for _, match in matches:
            print(f"  - {match.get('name', 'Unnamed project')}")
        return

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


def print_project_handoff(project_name):
    _, project, matches = resolve_project(project_name)

    if matches:
        print("More than one project matched. Please be more specific:")
        for _, match in matches:
            print(f"  - {match.get('name', 'Unnamed project')}")
        return

    if project is None:
        print(f"I do not have a project called '{project_name}' on the workboard yet.")
        return

    snapshot = get_latest_snapshot(project.get("name", project_name))

    print()
    print("Project handoff")
    print("================")
    print(f"Project: {project.get('name', project_name)}")
    print(f"Status: {project.get('status', 'active')}")
    print(f"Last thing finished: {project.get('last_finished', '') or 'not set'}")
    print(f"Blocker: {project.get('blocker', '') or 'none noted'}")
    print(f"Next step: {project.get('next_step', '') or 'not set'}")
    print(f"Priority: {project.get('priority', '') or 'not set'}")
    print()
    print("Latest snapshot:")
    if snapshot is None:
        print("  none saved for this project")
    else:
        print(f"  Time: {snapshot.get('created_at', 'unknown')}")
        print(f"  Where left off: {snapshot.get('summary', '') or 'not set'}")
        print(f"  Last finished: {snapshot.get('last_finished', '') or 'not set'}")
        print(f"  Blocker: {snapshot.get('blocker', '') or 'none noted'}")
        print(f"  Next step: {snapshot.get('next_step', '') or 'not set'}")
    print()
    print("Safety note: Keep this personal and local. Do not paste secrets, passwords, tokens, institutional private data, or private work information.")
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
    priority = input(f"Priority [{existing.get('priority', '')}]: ").strip() or existing.get("priority", "")
    return name, status, last_finished, blocker, next_step, priority


def run_add_project():
    print()
    print("Add project")
    _print_privacy_note()
    print()

    try:
        name, status, last_finished, blocker, next_step, priority = _prompt_project_fields()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Add project canceled.")
        return

    if not name:
        print("Project not saved. A name is required.")
        return

    _, project = upsert_project(name, status, last_finished, blocker, next_step, priority)
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

    _, existing, matches = resolve_project(project_name)
    if matches:
        print("More than one project matched. Please be more specific:")
        for _, match in matches:
            print(f"  - {match.get('name', 'Unnamed project')}")
        return

    if existing is None:
        print(f"I do not have '{project_name}' yet. Use addproject first.")
        return

    try:
        name, status, last_finished, blocker, next_step, priority = _prompt_project_fields(existing)
    except (KeyboardInterrupt, EOFError):
        print()
        print("Update project canceled.")
        return

    _, project = upsert_project(name, status, last_finished, blocker, next_step, priority)
    print(f"Updated project: {project['name']}")


def run_rename_project():
    print()
    print("Rename project")
    _print_privacy_note()
    print()

    projects = list_active_projects()
    if projects:
        print("Projects:")
        for _, project in projects:
            print(f"  - {project.get('name', 'Unnamed project')}")
        print()

    try:
        current_name = input("Current project name: ").strip()
        new_name = input("New project name: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Rename project canceled.")
        return

    status, result = rename_project(current_name, new_name)

    if status == "renamed":
        print(f"Renamed project to: {result['name']}")
        return

    if status == "ambiguous":
        print("More than one project matched. Please be more specific:")
        for _, project in result:
            print(f"  - {project.get('name', 'Unnamed project')}")
        return

    if status == "exists":
        print(f"A project called '{result.get('name', new_name)}' already exists.")
        return

    if status == "empty":
        print("Rename canceled. A new project name is required.")
        return

    print(f"I do not have '{current_name}' yet.")


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

from miso_core.identity import get_identity, print_identity
from miso_core.memory import forget, list_memories, recall, remember


def print_help():
    print()
    print("Miso commands:")
    print("  hello                  - Say hello")
    print("  status                 - Show Miso status")
    print("  remember <key> <value> - Save a local memory")
    print("  recall <key>           - Recall a local memory")
    print("  memories               - List saved memory keys")
    print("  forget <key>           - Delete a local memory")
    print("  help                   - Show this help menu")
    print("  exit                   - Close Miso")
    print()


def print_status():
    identity = get_identity()

    print()
    print("Miso status:")
    print(f"  Name: {identity['name']}")
    print(f"  Mode: {identity['mode']}")
    print(f"  Version: {identity['version']}")
    print(f"  Hardware: {identity['hardware']}")
    print(f"  Status: {identity['status']}")
    print()


def handle_remember(command):
    parts = command.split(maxsplit=2)

    if len(parts) < 3:
        print("Usage: remember <key> <value>")
        print("Example: remember favorite_color purple")
        return

    key = parts[1]
    value = parts[2]
    saved_key = remember(key, value)
    print(f"Okay, I remembered '{saved_key}'.")


def handle_recall(command):
    parts = command.split(maxsplit=1)

    if len(parts) < 2:
        print("Usage: recall <key>")
        return

    key = parts[1]
    value = recall(key)

    if value is None:
        print(f"I don't have a memory for '{key}' yet.")
    else:
        print(f"{key}: {value}")


def handle_memories():
    memories = list_memories()

    if not memories:
        print("I do not have any saved memories yet.")
        return

    print()
    print("Saved memory keys:")
    for key in sorted(memories.keys()):
        print(f"  - {key}")
    print()


def handle_forget(command):
    parts = command.split(maxsplit=1)

    if len(parts) < 2:
        print("Usage: forget <key>")
        return

    key = parts[1]

    if forget(key):
        print(f"I forgot '{key}'.")
    else:
        print(f"I did not have a memory for '{key}'.")


def run_cli():
    print_identity()
    print()
    print("Type 'help' to see what I can do.")

    while True:
        command = input("miso> ").strip()

        if command.lower() in ("exit", "quit", "q"):
            print("Goodbye from Miso.")
            break

        if command.lower() in ("help", "?"):
            print_help()
        elif command.lower() in ("hello", "hi"):
            print("Hi! I am Miso. I am awake and ready.")
        elif command.lower() == "status":
            print_status()
        elif command.lower().startswith("remember "):
            handle_remember(command)
        elif command.lower().startswith("recall "):
            handle_recall(command)
        elif command.lower() == "memories":
            handle_memories()
        elif command.lower().startswith("forget "):
            handle_forget(command)
        elif command == "":
            continue
        else:
            print(f"I don't know how to do '{command}' yet. Type 'help' for options.")

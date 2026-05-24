from miso_core.checkin import print_latest_checkin, run_checkin
from miso_core.identity import get_identity, print_identity
from miso_core.memory import forget, list_memories, recall, remember
from miso_core.responder import answer_question


EXIT_COMMANDS = {"exit", "quit", "close", "bye", "goodbye"}
HELLO_COMMANDS = {"hello", "hi", "hey"}


def print_help():
    print()
    print("Miso commands:")
    print("  hello                  - Say hello")
    print("  status                 - Show Miso status")
    print("  checkin                - Start a daily check-in")
    print("  lastcheckin            - Show the latest saved check-in")
    print("  ask <question>         - Ask Miso a simple offline question")
    print("  remember <key> <value> - Save a local memory")
    print("  recall <key>           - Recall a local memory")
    print("  memories               - List saved memory keys")
    print("  forget <key>           - Delete a local memory")
    print("  help                   - Show this help menu")
    print("  exit / close / bye     - Close Miso")
    print()
    print("Tip: You can also type a plain question, like:")
    print("  what can you help me do?")
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
        print("Use: remember <key> <value>")
        return

    key = parts[1]
    value = parts[2]
    remember(key, value)
    print(f"Okay, I remembered '{key}'.")


def handle_recall(command):
    parts = command.split(maxsplit=1)

    if len(parts) < 2:
        print("Use: recall <key>")
        return

    key = parts[1]
    value = recall(key)

    if value is None:
        print(f"I do not remember '{key}' yet.")
    else:
        print(f"{key}: {value}")


def handle_forget(command):
    parts = command.split(maxsplit=1)

    if len(parts) < 2:
        print("Use: forget <key>")
        return

    key = parts[1]

    if forget(key):
        print(f"I forgot '{key}'.")
    else:
        print(f"I did not have a memory called '{key}'.")


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


def handle_command(command):
    command = command.strip()
    command_lower = command.lower()

    if not command:
        return True

    if command_lower in EXIT_COMMANDS:
        print("Goodbye from Miso.")
        return False

    if command_lower in HELLO_COMMANDS:
        print("Hi! I am Miso. I am awake and ready.")
        return True

    if command_lower == "status":
        print_status()
        return True

    if command_lower == "help":
        print_help()
        return True

    if command_lower == "checkin":
        run_checkin()
        return True

    if command_lower in ("lastcheckin", "last checkin", "latest checkin"):
        print_latest_checkin()
        return True

    if command_lower.startswith("ask "):
        question = command[4:].strip()
        print(answer_question(question))
        return True

    if command_lower.startswith("remember "):
        handle_remember(command)
        return True

    if command_lower.startswith("recall "):
        handle_recall(command)
        return True

    if command_lower == "memories":
        handle_memories()
        return True

    if command_lower.startswith("forget "):
        handle_forget(command)
        return True

    print(answer_question(command))
    return True


def run_cli():
    print_identity()
    print()
    print("Type 'help' to see what I can do.")

    while True:
        try:
            command = input("miso> ")
        except KeyboardInterrupt:
            print()
            print("Goodbye from Miso.")
            break
        except EOFError:
            print()
            print("Goodbye from Miso.")
            break

        should_continue = handle_command(command)

        if not should_continue:
            break

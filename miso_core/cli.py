from miso_core.identity import get_identity, print_identity


def print_help():
    print()
    print("Miso commands:")
    print("  hello   - Say hello")
    print("  status  - Show Miso status")
    print("  help    - Show this help menu")
    print("  exit    - Close Miso")
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


def run_cli():
    print_identity()
    print()
    print("Type 'help' to see what I can do.")

    while True:
        command = input("miso> ").strip().lower()

        if command in ("exit", "quit", "q"):
            print("Goodbye from Miso.")
            break

        if command in ("help", "?"):
            print_help()
        elif command in ("hello", "hi"):
            print("Hi! I am Miso. I am awake and ready.")
        elif command == "status":
            print_status()
        elif command == "":
            continue
        else:
            print(f"I don't know how to do '{command}' yet. Type 'help' for options.")

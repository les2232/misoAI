def get_identity():
    return {
        "name": "Miso",
        "mode": "desk buddy",
        "version": "0.1.0",
        "hardware": "disabled for now",
        "status": "ready",
    }


def print_identity():
    identity = get_identity()

    print(f"Hello! I am {identity['name']}.")
    print(f"Mode: {identity['mode']}")
    print(f"Version: {identity['version']}")
    print(f"Hardware: {identity['hardware']}")
    print(f"Status: {identity['status']}")

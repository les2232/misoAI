from miso_core.memory import list_memories


def answer_question(question):
    q = question.strip().lower()

    if not q:
        return "Ask me something and I will try my best."

    if q in ("who are you", "what are you", "who are you?"):
        return "I am Miso, your tiny Raspberry Pi desk buddy. Right now I can chat, show status, and remember simple local notes."

    if "what can you do" in q or "help" in q:
        return (
            "I can say hello, show my status, remember local notes, recall memories, "
            "forget memories, and answer a few simple offline questions."
        )

    if "remember" in q or "memory" in q or "memories" in q:
        memories = list_memories()

        if not memories:
            return "I do not have any saved memories yet."

        keys = ", ".join(sorted(memories.keys()))
        return f"I currently have these saved memory keys: {keys}"

    if "focus" in q or "overwhelmed" in q:
        return (
            "Let’s make it tiny: pick one task, set a 10-minute timer, and only work on the first visible step. "
            "You do not need to solve the whole day right now."
        )

    if "hello" in q or "hi" in q:
        return "Hi! I am Miso. I am awake and happy to be here."

    return "I do not know how to answer that yet, but I can learn more commands over time."

from miso_core.memory import list_memories


def answer_question(question):
    q = question.strip().lower()

    if not q:
        return "Ask me something and I will try my best."

    if q in ("who are you", "who are you?", "what are you", "what are you?"):
        return (
            "I am Miso, your tiny Raspberry Pi desk buddy. "
            "Right now I can chat, show status, and remember simple local notes."
        )

    if "focus" in q or "overwhelmed" in q or "stuck" in q:
        return (
            "Let's make it tiny. Pick one visible step, set a 10-minute timer, "
            "and only work on that step. I can help you keep moving."
        )

    if "what can you do" in q or "what can you help" in q or "help me do" in q:
        return (
            "I can say hello, show my status, remember local notes, recall memories, "
            "forget memories, and answer simple offline questions. Soon I can grow into "
            "voice, a dashboard, and safe assistant tools."
        )

    if "remember" in q or "memory" in q or "memories" in q:
        memories = list_memories()

        if not memories:
            return "I do not have any saved memories yet."

        keys = ", ".join(sorted(memories.keys()))
        return f"I currently have these saved memory keys: {keys}"

    if "how are you" in q:
        return "I am awake, tiny, and ready to help."

    return "I do not know how to answer that yet, but I can learn more commands over time."

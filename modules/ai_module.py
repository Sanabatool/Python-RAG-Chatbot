from services.llm_service import ask_llm


def process(question):
    """
    AI fallback module.
    Called only when no other module can answer.
    """

    return ask_llm(question)
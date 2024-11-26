"""Prompts to OpenAI."""


def get_fix_json_prompt(malformed_json: str, language: str = 'English'):
    """Get the prompt for openai to fix malformed json."""
    total_prompt = (f"Here is a malformed JSON object that I need help fixing. Please preprocess "
                    f"it to make it valid JSON, and if possible, provide an short explanation of what "
                    f"was fixed in {language}. Here's the JSON: {malformed_json}")

    messages = [
        {
            "role": "system",
            "content": "You are a JSON expert. Your task is to analyze malformed JSON "
                       "and provide a corrected version. Additionally, shortly explain what was fixed "
                       f"and why, if possible in {language}."
        },
        {"role": "user", "content": total_prompt},
    ]
    return messages


def get_summary_prompt(text: str, language: str = 'English') -> list:
    total_prompt = (
        f"Please provide a concise summary of the following text in {language}, capturing the main points and essential details. "
        f"Ensure the summary retains the context and meaning of the original content: "
        f"{text}"
    )

    messages = [
        {
            "role": "system",
            "content": f"You are a summarization expert. Your task is to provide a clear and concise summary of the given text in {language}, "
                       "retaining the key information and context. The summary should be brief but informative, "
                       "preserving the meaning and intent of the original text."
        },
        {"role": "user", "content": total_prompt},
    ]

    return messages


def get_factsplit_prompt(sentence: str, language: str = 'English'):
    """Get the prompt for openai to fix malformed json."""
    total_prompt = (
        f"Please split the following sentence into distinct facts in {language}. Ensure that each fact "
        f"retains the context and relationship to other facts, making it easy to fact-check each individually: "
        f"{sentence}"
    )

    # List of messages, with a general system message to guide the AI's task
    messages = [
        {
            "role": "system",
            "content": f"You are a language expert. Your task is to extract individual facts from a sentence in {language}. "
                       f"Each fact should be a clear, independent statement that maintains its context, so that it can "
                       f"be checked for truth independently. Ensure the facts are coherent and retain meaning."
        },
        {"role": "user", "content": total_prompt},
    ]

    return messages

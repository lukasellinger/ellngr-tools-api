"""Prompts to OpenAI."""


def get_fix_json_prompt(malformed_json: str):
    """Get the prompt for openai to fix malformed json."""
    total_prompt = (f"Here is a malformed JSON object that I need help fixing. Please preprocess "
                    f"it to make it valid JSON, and if possible, provide an short explanation of what "
                    f"was fixed. Here's the JSON: {malformed_json}")

    messages = [
        {
            "role": "system",
            "content": "You are a JSON expert. Your task is to analyze malformed JSON "
                       "and provide a corrected version. Additionally, shortly explain what was fixed "
                       "and why, if possible."
        },
        {"role": "user", "content": total_prompt},
    ]
    return messages

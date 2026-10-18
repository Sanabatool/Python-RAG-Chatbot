import os
import requests
from dotenv import load_dotenv

load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# You can change this from .env later
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-4o-mini"
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_llm(prompt):
    """
    Send a prompt to OpenRouter and return the generated answer.
    """

    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not found in .env")

        return "AI service is not configured."


    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }


    data = {
        "model": OPENROUTER_MODEL,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": 0.2,

        "max_tokens": 500
    }


    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=data,
            timeout=60
        )


        print("\n========== OPENROUTER ==========")
        print("Status:", response.status_code)


        if response.status_code != 200:

            print("OpenRouter Error:")
            print(response.text)

            return "Sorry, I couldn't generate an answer right now."


        result = response.json()


        answer = (
            result
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content")
        )


        if not answer:

            print("No answer returned by OpenRouter.")

            return "Sorry, I couldn't generate an answer."


        return answer.strip()


    except requests.exceptions.Timeout:

        print("OpenRouter request timed out.")

        return "The AI service took too long to respond."


    except requests.exceptions.RequestException as e:

        print("OpenRouter connection error:", e)

        return "Unable to connect to the AI service."


    except Exception as e:

        print("Unexpected LLM error:", e)

        return "Something went wrong while generating the answer."
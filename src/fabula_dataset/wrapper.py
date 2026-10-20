import random
import json
import time
from typing import Any, Literal, TypeVar

from fabula_dataset.config import config
from google import genai
from google.genai import types
from pydantic import BaseModel
from openai import OpenAI

T = TypeVar("T", bound=BaseModel)


def sanitize_schema(schema: Any) -> Any:
    """Recursively removes 'additionalProperties' from a JSON schema dictionary."""
    if isinstance(schema, dict):
        return {
            k: sanitize_schema(v)
            for k, v in schema.items()
            if k != "additionalProperties"
        }
    elif isinstance(schema, list):
        return [sanitize_schema(v) for v in schema]
    return schema


def call_llm(
    prompt: str,
    model: Literal["gemini", "openrouter-gemini", "fanar-gemini"],
    response_schema: type[T] | None = None,
) -> T | str | None:
    match model:
        case "gemini":
            return call_gemini(prompt, response_schema)
        case "openrouter-gemini":
            return call_openrouter(prompt, response_schema)
        case "fanar-gemini":
            return call_fanar_gateway(prompt, response_schema)


def call_gemini(prompt: str, response_schema: type[T] | None = None) -> T | str | None:
    client = genai.Client(api_key=config.google_gemini_api_key)
    base_delay = 5
    attempts = 5

    # Prepare the sanitized schema dict for the API config if a Pydantic model was provided
    api_response_schema = None
    if response_schema:
        raw_schema = response_schema.model_json_schema()
        api_response_schema = sanitize_schema(raw_schema)

    for attempt in range(attempts):
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=api_response_schema,
                    temperature=0.2,
                ),
            )

            if not response.text:
                return None

            if response_schema:
                return response_schema.model_validate_json(response.text)
            return response.text

        except Exception as e:
            err_msg = str(e).lower()
            is_rate_limit = (
                "429" in err_msg
                or "503" in err_msg
                or "resource exhausted" in err_msg
                or "rate limit" in err_msg
                or "unavailable" in err_msg
            )
            if not is_rate_limit or attempt == attempts - 1:
                raise
            wait = base_delay * (2 * attempt)
            print(
                f"Rate limit hit, retrying in {wait}s (attempt {attempt + 1}/{attempts})..."
            )
            time.sleep(wait)

    return None


def call_fanar_gateway(
    prompt: str, response_schema: type[T] | None = None
) -> T | str | None:
    if response_schema:
        json_schema = json.dumps(response_schema.model_json_schema(), indent=2)
        prompt = (
            f"{prompt}\n"
            f"Respond ONLY with a single valid JSON object matching this exact schema:\n\n{json_schema}\n\n"
            f"No other text should be present in the response, return only the json object without any markdown formatting. "
            f"Avoid surrounding the json in backticks or '```json```'. Simply return the raw json."
        )

    client = OpenAI(
        base_url="https://ai-models-gw.fanar.qcri.org/v1",
        api_key=config.google_gemini_api_key,
    )

    response = client.chat.completions.create(
        model="gemini-3.8-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        seed=random.randint(0, 2**31 - 1),
    )

    content = response.choices[0].message.content
    if not content:
        return None

    # print("Raw Response - Fanar Gateway Gemini")
    # print(content)

    if response_schema:
        return response_schema.model_validate_json(content)
    return content


def call_openrouter(
    prompt: str, response_schema: type[T] | None = None
) -> T | str | None:
    if response_schema:
        json_schema = json.dumps(response_schema.model_json_schema(), indent=2)
        prompt = (
            f"{prompt}\n"
            f"Respond ONLY with a single valid JSON object matching this exact schema:\n\n{json_schema}\n\n"
            f"No other text should be present in the response, return only the json object without any markdown formatting. "
            f"Avoid surrounding the json in backticks or '```json```'. Simply return the raw json."
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=config.openrouter_api_key,
    )

    response = client.chat.completions.create(
        model="google/gemini-3.5-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        seed=random.randint(0, 2**31 - 1),
    )

    content = response.choices[0].message.content
    if not content:
        return None

    # print("Raw Response - OpenRouter Gemini")
    # print(content)

    if response_schema:
        return response_schema.model_validate_json(content)
    return content

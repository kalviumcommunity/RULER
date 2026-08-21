import os
import sys
import json
import logging
from typing import Tuple, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def mask_api_key(api_key: str) -> str:
    """Safely mask API key for logging output to prevent credential exposure."""
    if not api_key:
        return "<EMPTY>"
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]


def load_client_config_from_env(env_path: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Load and validate LLM API configuration strictly from environment variables (.env).
    
    Returns:
        Tuple[str, str, str]: (base_url, api_key, model_name)
    """
    if env_path:
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv(override=True)

    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE")
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")

    missing_vars = []
    if not base_url or not base_url.strip():
        missing_vars.append("OPENAI_BASE_URL")
    if not api_key or not api_key.strip():
        missing_vars.append("OPENAI_API_KEY")
    if not model_name or not model_name.strip():
        missing_vars.append("OPENAI_MODEL_NAME")

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables in configuration: {', '.join(missing_vars)}. "
            f"Please ensure they are defined in your .env file or environment."
        )

    return base_url.strip(), api_key.strip(), model_name.strip()


def build_llm_client(base_url: str, api_key: str) -> OpenAI:
    """Instantiate OpenAI-compatible client."""
    # Set max_retries=0 for instant error catching during test/validation runs
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        max_retries=1
    )


def initialize_client_from_env(env_path: Optional[str] = None) -> Tuple[OpenAI, str, str]:
    """Factory function to load env, log configuration safely, and return initialized client."""
    base_url, api_key, model_name = load_client_config_from_env(env_path)
    
    logger.info("-" * 50)
    logger.info("[CONFIG] Initializing Client Configuration from Environment")
    logger.info(f"   * Base URL: {base_url}")
    logger.info(f"   * Model:    {model_name}")
    logger.info(f"   * API Key:  {mask_api_key(api_key)}")
    logger.info("-" * 50)

    client = build_llm_client(base_url, api_key)
    return client, base_url, model_name


def send_chat_completion(
    client: OpenAI,
    model_name: str,
    system_prompt: str,
    user_prompt: str
) -> Optional[str]:
    """
    Send a chat completion request with system and user messages,
    log payloads and token usage, and cleanly handle API errors (401, 429, connection errors, etc.)
    with clear, human-readable messages instead of raw stack traces.
    
    Args:
        client (OpenAI): Initialized OpenAI client
        model_name (str): Target model identifier
        system_prompt (str): System message instructions
        user_prompt (str): User query/prompt
        
    Returns:
        Optional[str]: Model text reply content if successful, None if an error occurred.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Task 3: Log outgoing request payload
    request_payload = {
        "model": model_name,
        "messages": messages
    }
    logger.info("[OUTGOING REQUEST PAYLOAD]\n" + json.dumps(request_payload, indent=2))

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages
        )
    except AuthenticationError as e:
        logger.error(
            f"[AUTHENTICATION ERROR (401)] Authentication failed. "
            f"Please check that your OPENAI_API_KEY in .env is valid. Details: {e.message if hasattr(e, 'message') else e}"
        )
        return None
    except RateLimitError as e:
        logger.error(
            f"[RATE LIMIT EXCEEDED (429)] Rate limit or quota exceeded. "
            f"Please check your account plan or try again later. Details: {e.message if hasattr(e, 'message') else e}"
        )
        return None
    except APIConnectionError as e:
        logger.error(
            f"[CONNECTION ERROR] Failed to connect to LLM server at '{client.base_url}'. "
            f"Please verify that the LLM server is running and accessible."
        )
        return None
    except APIStatusError as e:
        logger.error(
            f"[API ERROR ({e.status_code})] Server returned error status {e.status_code}. "
            f"Details: {e.message if hasattr(e, 'message') else e}"
        )
        return None
    except Exception as e:
        logger.error(f"[UNEXPECTED API ERROR] An error occurred while communicating with the LLM API: {e}")
        return None

    # Task 3: Log incoming response payload
    try:
        response_dict = response.model_dump()
    except AttributeError:
        response_dict = dict(response) if hasattr(response, "__iter__") else str(response)

    logger.info("[INCOMING RESPONSE PAYLOAD]\n" + json.dumps(response_dict, indent=2, default=str))

    # Task 3: Log token usage if available
    if hasattr(response, "usage") and response.usage:
        usage = response.usage
        logger.info("[TOKEN USAGE]")
        logger.info(f"   * Prompt Tokens:     {getattr(usage, 'prompt_tokens', 'N/A')}")
        logger.info(f"   * Completion Tokens: {getattr(usage, 'completion_tokens', 'N/A')}")
        logger.info(f"   * Total Tokens:      {getattr(usage, 'total_tokens', 'N/A')}")

    # Extract model's text reply from choices[0].message.content
    reply_content = response.choices[0].message.content

    print("\n" + "=" * 50)
    print("[MODEL TEXT REPLY]")
    print(reply_content)
    print("=" * 50 + "\n")

    return reply_content


if __name__ == "__main__":
    try:
        client, base_url, model_name = initialize_client_from_env()
        
        system_prompt = "You are a helpful assistant for banking regulations and compliance."
        user_prompt = "What is the primary purpose of a banking regulatory compliance policy?"

        reply = send_chat_completion(
            client=client,
            model_name=model_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        if reply is None:
            sys.exit(1)

    except ValueError as e:
        logger.error(f"[CONFIG ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[UNEXPECTED ERROR] {e}")
        sys.exit(1)

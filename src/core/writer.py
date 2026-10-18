"""What writes the cards: the real LLM, or a stand-in on the stage profile."""

from typing import Any, cast

from openai import OpenAI

from core import config
from core.fake_llm import FakeLLM


def make_writer() -> OpenAI:
    """The writer for the profile in use (SU-3, SU-6). The real one needs OPENAI_API_KEY."""
    if config.FAKE_LLM:
        return cast(Any, FakeLLM())
    return OpenAI()

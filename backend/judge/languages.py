import os
from dataclasses import dataclass
from typing import Dict, List

from .enums import Language


@dataclass(frozen=True)
class LanguageConfig:
    language: str
    image: str
    source_filename: str
    binary_filename: str
    compile_command: List[str]
    run_command: List[str]
    compile_timeout_seconds: int = 10
    compile_memory_mb: int = 512


CPP17 = LanguageConfig(
    language=Language.CPP17.value,
    image=os.getenv("OJ_CPP_IMAGE", "gcc:13"),
    source_filename="main.cpp",
    binary_filename="main",
    compile_command=[
        "g++",
        "main.cpp",
        "-std=c++17",
        "-O2",
        "-pipe",
        "-o",
        "main",
    ],
    run_command=["./main"],
)


LANGUAGES: Dict[str, LanguageConfig] = {
    CPP17.language: CPP17,
}


def get_language_config(language: str) -> LanguageConfig:
    try:
        return LANGUAGES[language]
    except KeyError as exc:
        raise ValueError(f"Unsupported language: {language}") from exc

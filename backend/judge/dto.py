from dataclasses import dataclass


@dataclass
class CompileResult:
    success: bool
    exit_code: int
    output: str
    runtime_ms: int = 0
    system_error: bool = False


@dataclass
class DockerRunResult:
    exit_code: int
    runtime_ms: int
    memory_used_kb: int
    stdout: str
    stderr: str
    timed_out: bool = False
    memory_exceeded: bool = False
    output_exceeded: bool = False
    system_error: bool = False


@dataclass
class CaseJudgeResult:
    test_case_id: int
    verdict: str
    time_used_ms: int
    memory_used_kb: int
    message: str = ""

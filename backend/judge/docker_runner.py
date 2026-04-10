import re
import shlex
import subprocess
import time
from pathlib import Path
from typing import List, Sequence, Tuple

from django.conf import settings

from .dto import CompileResult, DockerRunResult
from .languages import LanguageConfig


TIME_PATTERN = re.compile(r"__OJ_TIME_SECONDS__=([0-9.]+)")
MEMORY_PATTERN = re.compile(r"__OJ_MEMORY_KB__=(\d+)")


class DockerRunner:
    """Thin Docker wrapper. Database state is intentionally handled elsewhere."""

    def __init__(self, output_limit_bytes: int = None) -> None:
        self.output_limit_bytes = output_limit_bytes or settings.JUDGE_OUTPUT_LIMIT_BYTES

    def compile(self, language: LanguageConfig, workdir: Path) -> CompileResult:
        command = "cd /workspace && " + shlex.join(language.compile_command)
        args = self._docker_args(
            image=language.image,
            memory_mb=language.compile_memory_mb,
            workdir=workdir,
            extra_mounts=[],
            command=command,
        )

        started_at = time.monotonic()
        try:
            completed = subprocess.run(
                args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=language.compile_timeout_seconds + 2,
            )
        except FileNotFoundError:
            return CompileResult(
                success=False,
                exit_code=-1,
                output="Docker executable was not found. Please install Docker and ensure it is in PATH.",
                system_error=True,
            )
        except subprocess.TimeoutExpired as exc:
            return CompileResult(
                success=False,
                exit_code=124,
                output=self._merge_timeout_output(exc),
                runtime_ms=int((time.monotonic() - started_at) * 1000),
            )

        output = (completed.stdout or "") + (completed.stderr or "")
        return CompileResult(
            success=completed.returncode == 0,
            exit_code=completed.returncode,
            output=output[-8000:],
            runtime_ms=int((time.monotonic() - started_at) * 1000),
        )

    def run_case(
        self,
        language: LanguageConfig,
        workdir: Path,
        testcase_root: Path,
        input_path: str,
        time_limit_ms: int,
        memory_limit_mb: int,
    ) -> DockerRunResult:
        input_in_container = "/testdata/" + input_path.replace("\\", "/").lstrip("/")
        inner_timeout_seconds = max(1, int(time_limit_ms / 1000) + 1)
        run_command = shlex.join(language.run_command)
        shell_command = (
            "cd /workspace && "
            f"/usr/bin/time -f '\\n__OJ_TIME_SECONDS__=%e\\n__OJ_MEMORY_KB__=%M' "
            f"timeout {inner_timeout_seconds}s {run_command} < {shlex.quote(input_in_container)}"
        )
        args = self._docker_args(
            image=language.image,
            memory_mb=memory_limit_mb,
            workdir=workdir,
            extra_mounts=[(testcase_root, "/testdata", "ro")],
            command=shell_command,
        )

        started_at = time.monotonic()
        try:
            completed = subprocess.run(
                args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=inner_timeout_seconds + 2,
            )
        except FileNotFoundError:
            return DockerRunResult(
                exit_code=-1,
                runtime_ms=0,
                memory_used_kb=0,
                stdout="",
                stderr="Docker executable was not found. Please install Docker and ensure it is in PATH.",
                system_error=True,
            )
        except subprocess.TimeoutExpired as exc:
            return DockerRunResult(
                exit_code=124,
                runtime_ms=int((time.monotonic() - started_at) * 1000),
                memory_used_kb=0,
                stdout=self._decode_timeout_text(exc.stdout),
                stderr=self._decode_timeout_text(exc.stderr),
                timed_out=True,
            )

        runtime_ms, memory_kb, clean_stderr = self._parse_time_and_memory(
            completed.stderr or "",
            fallback_runtime_ms=int((time.monotonic() - started_at) * 1000),
        )
        stdout, output_exceeded = self._truncate_stdout(completed.stdout or "")
        memory_exceeded = completed.returncode == 137 or memory_kb > memory_limit_mb * 1024

        return DockerRunResult(
            exit_code=completed.returncode,
            runtime_ms=runtime_ms,
            memory_used_kb=memory_kb,
            stdout=stdout,
            stderr=clean_stderr[-4000:],
            timed_out=completed.returncode == 124,
            memory_exceeded=memory_exceeded,
            output_exceeded=output_exceeded,
        )

    def _docker_args(
        self,
        image: str,
        memory_mb: int,
        workdir: Path,
        extra_mounts: Sequence[Tuple[Path, str, str]],
        command: str,
    ) -> List[str]:
        args = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--memory",
            f"{memory_mb}m",
            "--cpus",
            "1.0",
            "--pids-limit",
            "128",
            "-v",
            f"{workdir.resolve()}:/workspace:rw",
        ]
        for host_path, container_path, mode in extra_mounts:
            args.extend(["-v", f"{host_path.resolve()}:{container_path}:{mode}"])
        args.extend([image, "sh", "-lc", command])
        return args

    def _parse_time_and_memory(self, stderr: str, fallback_runtime_ms: int) -> Tuple[int, int, str]:
        time_match = TIME_PATTERN.search(stderr)
        memory_match = MEMORY_PATTERN.search(stderr)

        runtime_ms = fallback_runtime_ms
        if time_match:
            runtime_ms = int(float(time_match.group(1)) * 1000)

        memory_kb = 0
        if memory_match:
            memory_kb = int(memory_match.group(1))

        clean_stderr = TIME_PATTERN.sub("", stderr)
        clean_stderr = MEMORY_PATTERN.sub("", clean_stderr).strip()
        return runtime_ms, memory_kb, clean_stderr

    def _truncate_stdout(self, stdout: str) -> Tuple[str, bool]:
        encoded = stdout.encode("utf-8", errors="replace")
        if len(encoded) <= self.output_limit_bytes:
            return stdout, False

        truncated = encoded[: self.output_limit_bytes].decode("utf-8", errors="replace")
        return truncated, True

    def _merge_timeout_output(self, exc: subprocess.TimeoutExpired) -> str:
        return (self._decode_timeout_text(exc.stdout) + self._decode_timeout_text(exc.stderr))[-8000:]

    def _decode_timeout_text(self, value) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value)

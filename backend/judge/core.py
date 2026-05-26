import shutil
from pathlib import Path
from typing import Iterable, List

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from oj.models import Submission, SubmissionCaseResult, TestCase

from .compare import compare_output
from .docker_runner import DockerRunner
from .dto import CaseJudgeResult, DockerRunResult
from .enums import SubmissionStatus, Verdict
from .languages import get_language_config


class JudgeCore:
    def __init__(self, runner: DockerRunner = None) -> None:
        self.runner = runner or DockerRunner()
        self.testcase_root = Path(settings.TESTCASE_ROOT).resolve()
        self.work_root = Path(settings.JUDGE_WORK_ROOT).resolve()

    def judge_submission(self, submission_id: int) -> Submission:
        # 一次提交的完整判题流程：取提交数据 -> 编译 -> 跑每个测试点 -> 汇总最终结果。
        submission = Submission.objects.select_related("problem", "user").get(pk=submission_id)
        language = get_language_config(submission.language)
        test_cases = list(submission.problem.test_cases.order_by("sort_order", "id"))

        # 没有测试点时无法判断答案正确性，按系统错误结束，方便管理员排查题目配置。
        if not test_cases:
            return self._finish_submission(submission, Verdict.SE.value, "No test cases configured.")

        workdir = self._prepare_workdir(submission.id)
        source_path = workdir / language.source_filename
        # 用户源码只写入本次提交的临时目录，后续编译和运行都在这个目录内完成。
        source_path.write_text(submission.source_code, encoding="utf-8")

        SubmissionCaseResult.objects.filter(submission=submission).delete()
        compile_result = self.runner.compile(language, workdir)
        if compile_result.system_error:
            return self._finish_submission(submission, Verdict.SE.value, compile_result.output)

        if not compile_result.success:
            return self._finish_submission(submission, Verdict.CE.value, compile_result.output)

        case_results: List[CaseJudgeResult] = []
        for test_case in test_cases:
            # 每个测试点独立运行，避免前一个测试点的进程或文件影响后一个测试点。
            case_result = self._judge_case(submission, test_case, language, workdir)
            case_results.append(case_result)
            SubmissionCaseResult.objects.update_or_create(
                submission=submission,
                test_case_id=case_result.test_case_id,
                defaults={
                    "verdict": case_result.verdict,
                    "time_used_ms": case_result.time_used_ms,
                    "memory_used_kb": case_result.memory_used_kb,
                    "message": case_result.message,
                },
            )

        final_verdict = self._aggregate_verdict(case_results)
        submission.final_verdict = final_verdict
        submission.status = SubmissionStatus.FINISHED.value
        submission.total_time_ms = sum(result.time_used_ms for result in case_results)
        submission.max_memory_kb = max((result.memory_used_kb for result in case_results), default=0)
        submission.compile_log = ""
        submission.judged_at = timezone.now()
        submission.save(
            update_fields=[
                "final_verdict",
                "status",
                "total_time_ms",
                "max_memory_kb",
                "compile_log",
                "judged_at",
            ]
        )
        return submission

    def _judge_case(self, submission: Submission, test_case: TestCase, language, workdir: Path) -> CaseJudgeResult:
        self._safe_testcase_path(test_case.input_path)
        expected_path = self._safe_testcase_path(test_case.output_path)
        expected_output = expected_path.read_text(encoding="utf-8", errors="replace")

        run_result = self.runner.run_case(
            language=language,
            workdir=workdir,
            testcase_root=self.testcase_root,
            input_path=test_case.input_path,
            time_limit_ms=submission.problem.time_limit_ms,
            memory_limit_mb=submission.problem.memory_limit_mb,
        )
        verdict = self._case_verdict(run_result, expected_output, submission.problem.time_limit_ms, submission.problem.memory_limit_mb)
        return CaseJudgeResult(
            test_case_id=test_case.id,
            verdict=verdict,
            time_used_ms=run_result.runtime_ms,
            memory_used_kb=run_result.memory_used_kb,
            message=self._case_message(verdict, run_result),
        )

    def _case_verdict(
        self,
        run_result: DockerRunResult,
        expected_output: str,
        time_limit_ms: int,
        memory_limit_mb: int,
    ) -> str:
        # 判题结果按传统 OJ 优先级判断：系统错误 -> 超时 -> 超内存 -> 输出过多 -> 运行错误 -> AC/WA。
        if run_result.system_error:
            return Verdict.SE.value
        if run_result.timed_out or run_result.runtime_ms > time_limit_ms:
            return Verdict.TLE.value
        if run_result.memory_exceeded or run_result.memory_used_kb > memory_limit_mb * 1024:
            return Verdict.MLE.value
        if run_result.output_exceeded:
            return Verdict.OLE.value
        if run_result.exit_code != 0:
            return Verdict.RE.value
        if compare_output(run_result.stdout, expected_output):
            return Verdict.AC.value
        return Verdict.WA.value

    def _case_message(self, verdict: str, run_result: DockerRunResult) -> str:
        if verdict == Verdict.AC.value:
            return ""
        if verdict == Verdict.WA.value:
            return "Output differs from the expected answer."
        if verdict == Verdict.OLE.value:
            return "Program output exceeded the configured output limit."
        if verdict == Verdict.TLE.value:
            return "Program exceeded the time limit."
        if verdict == Verdict.MLE.value:
            return "Program exceeded the memory limit."
        if run_result.stderr:
            return run_result.stderr[-1000:]
        return f"Process exited with code {run_result.exit_code}."

    def _aggregate_verdict(self, results: Iterable[CaseJudgeResult]) -> str:
        # 按测试点顺序返回第一个非 AC 结果；全部通过才算整题 AC。
        seen_any = False
        for result in results:
            seen_any = True
            if result.verdict != Verdict.AC.value:
                return result.verdict
        return Verdict.AC.value if seen_any else Verdict.SE.value

    def _finish_submission(self, submission: Submission, verdict: str, compile_log: str = "") -> Submission:
        submission.final_verdict = verdict
        submission.status = SubmissionStatus.FINISHED.value
        submission.compile_log = compile_log[-8000:]
        submission.total_time_ms = 0
        submission.max_memory_kb = 0
        submission.judged_at = timezone.now()
        submission.save(
            update_fields=[
                "final_verdict",
                "status",
                "compile_log",
                "total_time_ms",
                "max_memory_kb",
                "judged_at",
            ]
        )
        return submission

    def _prepare_workdir(self, submission_id: int) -> Path:
        # 每次提交在宿主机上使用独立工作目录，便于清理并避免不同提交相互覆盖。
        self.work_root.mkdir(parents=True, exist_ok=True)
        workdir = (self.work_root / f"submission_{submission_id}").resolve()
        if self.work_root not in workdir.parents:
            raise ValueError("Resolved workdir is outside JUDGE_WORK_ROOT.")
        if workdir.exists():
            shutil.rmtree(workdir)
        workdir.mkdir(parents=True)
        return workdir

    def _safe_testcase_path(self, relative_path: str) -> Path:
        # 测试点路径必须留在 TESTCASE_ROOT 内，防止通过 ../ 访问到目录外文件。
        target = (self.testcase_root / relative_path).resolve()
        if target != self.testcase_root and self.testcase_root not in target.parents:
            raise ValueError(f"Testcase path escapes TESTCASE_ROOT: {relative_path}")
        if not target.exists():
            raise FileNotFoundError(f"Testcase file does not exist: {relative_path}")
        return target


def judge_submission(submission_id: int) -> Submission:
    # 行锁用于防止多个 worker 同时抢到同一条提交记录。
    with transaction.atomic():
        submission = Submission.objects.select_for_update().get(pk=submission_id)
        if submission.status != SubmissionStatus.JUDGING.value:
            submission.status = SubmissionStatus.JUDGING.value
            submission.save(update_fields=["status"])

    return JudgeCore().judge_submission(submission_id)

import logging
import time
from typing import Optional

from django.db import connection, transaction
from django.utils import timezone

from oj.models import Submission

from .core import JudgeCore
from .enums import SubmissionStatus, Verdict


logger = logging.getLogger(__name__)


class JudgeWorker:
    def __init__(self, sleep_seconds: float = 2.0) -> None:
        self.sleep_seconds = sleep_seconds
        self.core = JudgeCore()

    def run_once(self) -> bool:
        submission = self.claim_next_submission()
        if submission is None:
            return False

        try:
            self.core.judge_submission(submission.id)
        except Exception as exc:
            logger.exception("Judge failed for submission %s", submission.id)
            self.mark_system_error(submission.id, exc)
        return True

    def run_forever(self) -> None:
        while True:
            did_work = self.run_once()
            if not did_work:
                # 队列为空时短暂休眠，避免空轮询长期占用 CPU。
                time.sleep(self.sleep_seconds)

    def claim_next_submission(self) -> Optional[Submission]:
        with transaction.atomic():
            # 优先领取最早进入队列的提交；select_for_update 用来避免多 worker 重复领取。
            queryset = Submission.objects.filter(status=SubmissionStatus.QUEUED.value).order_by("submitted_at", "id")
            if connection.features.has_select_for_update:
                queryset = queryset.select_for_update(skip_locked=connection.features.has_select_for_update_skip_locked)

            submission = queryset.first()
            if submission is None:
                return None

            submission.status = SubmissionStatus.JUDGING.value
            submission.save(update_fields=["status"])
            return submission

    def mark_system_error(self, submission_id: int, exc: Exception) -> None:
        # worker 自身异常时也要给提交写入最终状态，避免一直停在 JUDGING。
        Submission.objects.filter(pk=submission_id).update(
            status=SubmissionStatus.FINISHED.value,
            final_verdict=Verdict.SE.value,
            compile_log=str(exc)[-8000:],
            judged_at=timezone.now(),
        )

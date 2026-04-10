from django.core.management.base import BaseCommand

from judge.worker import JudgeWorker


class Command(BaseCommand):
    help = "Run the simple OJ judge worker."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true", help="Process at most one queued submission and exit.")
        parser.add_argument("--sleep", type=float, default=2.0, help="Seconds to sleep when the queue is empty.")

    def handle(self, *args, **options):
        worker = JudgeWorker(sleep_seconds=options["sleep"])
        if options["once"]:
            did_work = worker.run_once()
            self.stdout.write("processed one submission" if did_work else "queue is empty")
            return

        self.stdout.write("judge worker started")
        worker.run_forever()

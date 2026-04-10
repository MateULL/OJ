from enum import Enum
from typing import List, Tuple


class ChoiceEnum(str, Enum):
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(item.value, item.value) for item in cls]


class JudgeMode(ChoiceEnum):
    STANDARD = "standard"


class Language(ChoiceEnum):
    CPP17 = "cpp17"


class SubmissionStatus(ChoiceEnum):
    QUEUED = "QUEUED"
    JUDGING = "JUDGING"
    FINISHED = "FINISHED"


class Verdict(ChoiceEnum):
    AC = "AC"
    WA = "WA"
    CE = "CE"
    RE = "RE"
    TLE = "TLE"
    MLE = "MLE"
    OLE = "OLE"
    SE = "SE"

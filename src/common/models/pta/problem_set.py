from typing import Any, Dict, List

from pydantic import BaseModel


class ProblemSetConfig(BaseModel):
    compilers: List[str]
    multipleChoiceMoreThanOneAnswerProblemScoringMethod: str
    scoringRule: str
    hideScoreboard: bool
    hidingTime: int
    showNameInRanking: bool
    hideOtherProblemSets: bool
    allowStudentLogin: bool
    allowedLoginSecondsBeforeStart: int
    omsProtected: bool
    allowSubmitExam: bool
    problemTypeOrder: List[str]
    useStrictCodeJudger: bool
    showBulletinBoard: bool
    showDetections: bool
    examGroupId: str
    enableCustomTestData: bool
    enableVirtualPrinter: bool
    blindJudgeSubjective: bool
    autoSave: bool
    forbidPasting: bool
    allowAddCollection: bool
    allowFilterUserGroup: bool
    hasGrading: bool
    enableXcpcContestService: bool
    collectionDerivedProblemSetId: str
    showDifficulty: bool
    postPayAccountId: str
    postPayAccountType: str
    hideProgrammingJudgeResponseContents: bool
    hideScore: bool
    enableAi: bool
    enableCompetitionService: bool


class _ProblemSet(BaseModel):
    id: str
    name: str
    description: str
    type: str
    timeType: str
    problemSetConfig: ProblemSetConfig
    startAt: str
    endAt: str
    duration: int
    shareCode: str
    manageable: bool
    collaboratorPermission: str
    ownerOrganizationId: str
    ownerId: str
    hide: bool
    stage: str
    announcement: str
    internal: bool
    feature: str
    batchJudgeAt: str
    connections: Dict[str, Any]
    archived: bool


class ProblemSet(BaseModel):
    problemSet: _ProblemSet
    favorites: List[Any]
    collaboratorPermission: str
    shareCode: str
    user: Dict[str, Any]
    organization: Dict[str, Any]

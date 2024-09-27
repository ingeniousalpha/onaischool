from apps.common.exceptions import BaseAPIException
from config.constants.error_codes import (
    ANSWER_DOESNT_EXISTS, EXAM_NOT_FOUND,
    QUESTION_NOT_FOUND, YOU_CANNOT_FINISH_QUIZ,
INVALID_ASSESSMENT_INPUT
)


class AnswerDoesntExists(BaseAPIException):
    status_code = 400
    default_code = ANSWER_DOESNT_EXISTS


class ExamNotFound(BaseAPIException):
    status_code = 400
    default_code = EXAM_NOT_FOUND


class QuestionNotFound(BaseAPIException):
    status_code = 400
    default_code = QUESTION_NOT_FOUND


class YouCannotFinishQuiz(BaseAPIException):
    status_code = 400
    default_code = YOU_CANNOT_FINISH_QUIZ


class InvalidAssessmentInput(BaseAPIException):
    status_code = 400
    default_code =INVALID_ASSESSMENT_INPUT

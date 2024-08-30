from apps.common.exceptions import BaseAPIException
from config.constants.error_codes import (
    ANSWER_DOESNT_EXISTS, EXAM_NOT_FOUND
)


class AnswerDoesntExists(BaseAPIException):
    status_code = 400
    default_code = ANSWER_DOESNT_EXISTS


class ExamNotFound(BaseAPIException):
    status_code = 400
    default_code = EXAM_NOT_FOUND

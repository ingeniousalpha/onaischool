from apps.common.exceptions import BaseAPIException
from config.constants.error_codes import TOPIC_NOT_FOUND


class TopicNotFound(BaseAPIException):
    status_code = 400
    default_code = TOPIC_NOT_FOUND

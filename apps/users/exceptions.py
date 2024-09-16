from apps.common.exceptions import BaseAPIException
from config.constants.error_codes import (
    PASSWORD_MIN_LENGTH, PASSWORDS_ARE_NOT_EQUAL, PASSWORD_INVALID, AVATAR_NOT_FOUND,
    CURRENTPASSWORD_AND_NEWPASSWORD_EQUAL
)


class PasswordMinLength(BaseAPIException):
    status_code = 400
    default_code = PASSWORD_MIN_LENGTH


class PasswordsAreNotEqual(BaseAPIException):
    status_code = 400
    default_code = PASSWORDS_ARE_NOT_EQUAL


class PasswordInvalid(BaseAPIException):
    status_code = 400
    default_code = PASSWORD_INVALID


class NewPasswordInvalid(BaseAPIException):
    status_code = 400
    default_code = CURRENTPASSWORD_AND_NEWPASSWORD_EQUAL


class AvatarNotFound(BaseAPIException):
    status_code = 400
    default_code = AVATAR_NOT_FOUND

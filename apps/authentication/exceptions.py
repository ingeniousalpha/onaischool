from apps.common.exceptions import BaseAPIException
from config.constants.error_codes import (
    USER_NOT_FOUND,
    USER_ALREADY_EXISTS,
    INVALID_OTP,
    USER_ALREADY_HAS_ACTIVE_BOOKING,
    NOT_APPROVED_USER_CAN_NOT_BOOK_SEVERAL_COMPUTERS,
    NOT_SUFFICIENT_CASHBACK_AMOUNT,
    SCHOOL_NOT_FOUND,
    INCORRECT_PASSWORD,
    ACCESS_DENIED
)


class UserNotFound(BaseAPIException):
    status_code = 400
    default_code = USER_NOT_FOUND


class SchoolNotFound(BaseAPIException):
    status_code = 400
    default_code = SCHOOL_NOT_FOUND


class UserAlreadyHasActiveBooking(BaseAPIException):
    status_code = 400
    default_code = USER_ALREADY_HAS_ACTIVE_BOOKING


class NotApprovedUserCanNotBookSeveralComputers(BaseAPIException):
    status_code = 400
    default_code = NOT_APPROVED_USER_CAN_NOT_BOOK_SEVERAL_COMPUTERS


class NotSufficientCashbackAmount(BaseAPIException):
    status_code = 400
    default_code = NOT_SUFFICIENT_CASHBACK_AMOUNT


class UserAlreadyExists(BaseAPIException):
    status_code = 400
    default_code = USER_ALREADY_EXISTS


class InvalidOTP(BaseAPIException):
    status_code = 400
    default_code = INVALID_OTP


class InCorrectPassword(BaseAPIException):
    status_code = 400
    default_code = INCORRECT_PASSWORD


class AccessDenied(BaseAPIException):
    status_code = 400
    default_code = ACCESS_DENIED

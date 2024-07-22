from .error_codes import *
ERROR_MESSAGES = {
    INTERNAL_SERVER_ERROR: ("INTERNAL_SERVER_ERROR_MSG", ""),
    TOO_MANY_REQUEST: ("TOO_MANY_REQUEST_RU_MSG", ""),
    INVALID_INPUT_DATA: ("INVALID_INPUT_DATA_RU_MSG", ""),
    NOT_FOUND: ("NOT_FOUND_RU_MSG", ""),
    USER_NOT_FOUND: ("USER_NOT_FOUND_RU_MSG", ""),
    USER_ALREADY_EXISTS: ("USER_ALREADY_EXISTS_RU_MSG", ""),
    USER_NOT_AUTHORIZED: ("USER_NOT_AUTHORIZED_RU_MSG", ""),
    USER_DOES_NOT_HAVE_PHONE_NUMBER: ("USER_DOES_NOT_HAVE_PHONE_NUMBER", ""),
    USER_INACTIVE: ("USER_INACTIVE_RU_MSG", ""),
    TOKEN_EXPIRED: ("TOKEN_EXPIRED_RU_MSG", ""),
    INVALID_OTP: ("INVALID_OTP_RU_MSG", ""),
    OTP_RESEND_TIME_LIMIT: ("OTP_RESEND_TIME_LIMIT_RU_MSG", ""),
    PASSWORD_MIN_LENGTH: ("PASSWORD_MIN_LENGTH_8_RU_MSG", ""),
    PASSWORDS_ARE_NOT_EQUAL: ("PASSWORDS_ARE_NOT_EQUAL_RU_MSG", ""),
    PASSWORD_INVALID: ("PASSWORD_INVALID_RU_MSG", ""),
    # f"{EMAIL_CONFIRMATION_EXPIRED}_{Languages.RUSSIAN}": ("email confirmation link expired ru", ""),
    EMAIL_ALREADY_CONFIRMED: ("EMAIL_ALREADY_CONFIRMED ru", ""),
    CLUB_BRANCH_NOT_FOUND: ("CLUB_BRANCH_NOT_FOUND_MSG", ""),
    BOOKING_NOT_FOUND: ("BOOKING_NOT_FOUND_MSG", ""),
    NEED_TO_INPUT_USER_LOGIN: ("NEED_TO_INPUT_USER_LOGIN_MSG", ""),
    GIZMO_LOGIN_ALREADY_EXISTS_ERROR: ("Such login already exists in the club", ""),
    BOOKING_STATUS_IS_NOT_APPROPRIATE: ("BOOKING_STATUS_IS_NOT_APPROPRIATE_MSG", ""),
    USER_NEED_TO_VERIFY_IIN: ("USER_NEED_TO_VERIFY_IIN_MSG", ""),
    ONEVISION_SERVICE_INPUT_DATA_INVALID: ("ONEVISION_SERVICE_INPUT_DATA_INVALID", ""),
    NOT_APPROVED_USER_CAN_NOT_BOOK_SEVERAL_COMPUTERS: ("NOT_APPROVED_USER_CAN_NOT_BOOK_SEVERAL_COMPUTERS", ""),
    NOT_SUFFICIENT_CASHBACK_AMOUNT: ("NOT_SUFFICIENT_CASHBACK_AMOUNT", ""),
}


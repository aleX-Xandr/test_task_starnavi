import enum


@enum.unique
class ContentTypeEnum(str, enum.Enum):
    JSON = "application/json"
    FORM = "multipart/form-data"
    QUERY = "application/x-www-form-urlencoded"

PASSWORD = "test_pass"

# Meaningful text is required for correct testing
TEXT = "Today I'm going to the Leonardo da Vinci Museum."
BAD_TEXT = "Today I'm going to suck a dick."

import enum


@enum.unique
class ContentTypeEnum(str, enum.Enum):
    JSON = "application/json"
    FORM = "multipart/form-data"
    QUERY = "application/x-www-form-urlencoded"

PASSWORD = "test_pass"

import enum


@enum.unique
class ContentTypeEnum(str, enum.Enum):
    JSON = "application/json"
    FORM = "multipart/form-data"

PASSWORD = "test_pass"

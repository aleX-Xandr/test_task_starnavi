import enum


@enum.unique
class ScopeEnum(str, enum.Enum):
    ACCOUNT_GET = "account:get"

    POSTS_GET = "posts:get"
    POSTS_CREATE = "posts:create"
    POSTS_UPDATE = "posts:update"
    POSTS_DELETE = "posts:delete"
    
    COMMENTS_GET = "comments:get"
    COMMENTS_CREATE = "comments:create"
    COMMENTS_UPDATE = "comments:update"
    COMMENTS_DELETE = "comments:delete"

    STATISTICS_GET = "statistics:get"
    

@enum.unique
class RolePermissionsEnum(str, enum.Enum):
    USER = f"account:* posts:* comments:*"
    ADMIN = f"{USER} statistics:*"


@enum.unique
class RoleEnum(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

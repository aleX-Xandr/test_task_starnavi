import enum

from typing import List, TypedDict, Union


class DeepDictList(TypedDict):
    key: List[Union["DeepDictList", dict[str, str]]]


@enum.unique
class PostStatusEnum(str, enum.Enum):
    BANNED = "BANNED"
    NOT_BANNED = "NOT_BANNED"

RESPOND_EXACTLY = lambda value: f"respond with exactly \"{value}\" (no additional text or symbols)"

PROMPT = lambda generate_answer: """
You are an AI responsible for moderating posts and comments in an online forum. Your task is to evaluate user-generated content in real-time for offensive language, such as profanity, abusive language, or any form of insult.

TASK:
1. **If the content contains any offensive language**, {banned}.
2. **If the content is free of offensive language**, {not_banned}.

Please analyze the following content and respond based on the instructions above.
""".format(
    banned=RESPOND_EXACTLY(PostStatusEnum.BANNED.value),
    not_banned=(
        "generate a relevant and thoughtful reply that aligns with context of the post and comment"
        if generate_answer else
        RESPOND_EXACTLY(PostStatusEnum.NOT_BANNED.value)
    )
)

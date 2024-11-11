import enum


@enum.unique
class PostStatusEnum(str, enum.Enum):
    BANNED = "BANNED"
    ALLOWED = "ALLOWED"

RESPOND_EXACTLY = lambda value: f"respond with exactly \"{value}\" "\
                                "(no additional text or symbols)"

PROMPT_TEMPLATE = "You are an AI responsible for moderating posts and "\
    "comments in an online forum. Your task is to evaluate user-generated "\
    "content in real-time for offensive language, such as profanity, "\
    "abusive language, or any form of insult.\n\n"\
    "TASK:\n"\
    "1. **If the content contains any offensive language**, {banned}.\n"\
    "2. **If the content is free of offensive language**, {not_banned}.\n\n"\
    "Please respond based on the instructions above and analyze "\
    "the following content:"
    
PROMPT = lambda generate_answer: PROMPT_TEMPLATE.format(
    banned=RESPOND_EXACTLY(PostStatusEnum.BANNED.value),
    not_banned=(
        "generate a relevant and thoughtful reply that aligns "\
        "with context of the post and comment"
        if generate_answer else
        RESPOND_EXACTLY(PostStatusEnum.ALLOWED.value)
    )
)

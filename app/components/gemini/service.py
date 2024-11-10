from httpx import AsyncClient

from app.components.comments.models import Comment
from app.components.gemini.consts import DeepDictList, PROMPT, PostStatusEnum
from app.components.posts.models import Post
from app.configs import GeminiConfig



class GeminiService: # TODO response status and tokens limit checker
    headers = {
        "Content-Type": "application/json"
    }

    def __init__(
        self,
        config: GeminiConfig
    ):
        self._config = config

    @property
    def api_endpoint(self) -> str:
        return "https://generativelanguage.googleapis.com/v1beta/models/" \
              f"gemini-1.5-flash:generateContent?key={self._config.api_key}"
    
    @staticmethod
    def make_payload(
        text: str, 
        generate_answer: bool = False
    ) -> DeepDictList:
        return {
            "contents": [
                {
                    "parts": [
                        {"text": PROMPT(generate_answer)},
                        {"text": f"{text}"}
                    ]
                }
            ],
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_CIVIC_INTEGRITY",
                    "threshold": "BLOCK_NONE"
                },
            ],
        }
    
    @staticmethod
    def process_result(response: dict) -> bool | str:
        best_candidate = response["candidates"][0]
        analyze_result = best_candidate["content"]["parts"][0]["text"]
        if PostStatusEnum.NOT_BANNED.value in analyze_result:
            return True
        if PostStatusEnum.BANNED.value in analyze_result:
            return False
        return analyze_result

    async def call_api(self, payload: DeepDictList) -> dict:
        async with AsyncClient(headers=self.headers) as client:
            response = await client.post(self.api_endpoint, json=payload)
            return response.json()

    async def analyze_text(self, text: str, is_auto_comment: bool = False) -> bool | str:
        payload = self.make_payload(text, is_auto_comment)
        response = await self.call_api(payload)
        return self.process_result(response)
        
    async def analyze_comment(
        self, 
        post: Post, 
        comment: Comment
    ) -> bool | str:
        is_auto_comment = isinstance(post.auto_comment_timeout, int)
        text = f"POST: {post.text}\n\nCOMMENT: {comment.text}"
        return await self.analyze_text(text, is_auto_comment)

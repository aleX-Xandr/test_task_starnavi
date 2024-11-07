import httpx
import asyncio

async def register_user(username: str, password: str):
    url = "http://localhost:8000/accounts/register"
    payload = {
        "username": username,
        "password": password
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/accounts/register", data=payload)
        
        if response.status_code == 200:
            print("Успешная регистрация:", response.json())
        else:
            print(f"Ошибка: {response.status_code} - {response.text}")
            return
        
        response = await client.post("http://localhost:8000/auth/token", data=payload)
        if response.status_code == 200:
            print("Успешная авторизация:", response.json())
        else:
            print(f"Ошибка: {response.status_code} - {response.text}")
            return

if __name__ == "__main__":
    asyncio.run(register_user("TestUser", "TestPass"))

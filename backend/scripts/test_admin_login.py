
import asyncio
import os
import sys
import httpx
from pathlib import Path

async def test_login():
    password = os.getenv("NSPOX_ADMIN_PASSWORD")
    if not password:
        raise RuntimeError("Set NSPOX_ADMIN_PASSWORD before testing admin login.")

    url = "http://localhost:8000/api/v1/admin/auth/login"
    data = {
        "username": "admin",
        "password": password
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            if response.status_code == 200:
                print("✅ Login successful")
            else:
                print("❌ Login failed")
        except Exception as e:
            print(f"❌ Error connecting to server: {e}")

if __name__ == "__main__":
    asyncio.run(test_login())

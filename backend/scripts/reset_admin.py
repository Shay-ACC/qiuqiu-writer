
import asyncio
import sys
import os
from pathlib import Path

# Add src to python path
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

# 避免导入整个memos包，直接导入需要的模块
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import bcrypt

DATABASE_URL_ENV = "DATABASE_URL"
ADMIN_PASSWORD_ENV = "NSPOX_ADMIN_PASSWORD"
LEGACY_WEAK_ADMIN_PASSWORD = "admin" + "123456"
WEAK_ADMIN_PASSWORDS = {
    "",
    "example-placeholder-do-not-use",
}


def get_required_database_url():
    database_url = os.getenv(DATABASE_URL_ENV)
    if not database_url:
        raise RuntimeError(f"Set {DATABASE_URL_ENV} before resetting the admin password.")
    return database_url


def get_required_admin_password():
    password = os.getenv(ADMIN_PASSWORD_ENV, "")
    if password in WEAK_ADMIN_PASSWORDS or password == LEGACY_WEAK_ADMIN_PASSWORD:
        raise RuntimeError(
            f"Set {ADMIN_PASSWORD_ENV} to a strong password before resetting the admin password."
        )
    return password

# 简化的AdminUser模型
class AdminUser:
    __tablename__ = "admin_users"
    
    def __init__(self, id=None, username=None, password_hash=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash

def get_password_hash(password):
    """生成密码哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def get_async_session():
    """创建异步会话"""
    engine = create_async_engine(get_required_database_url())
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session
    await engine.dispose()

async def reset_admin():
    # 创建异步引擎
    new_password = get_required_admin_password()
    engine = create_async_engine(get_required_database_url())
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        try:
            # 直接使用原始SQL查询
            result = await session.execute(
                text("SELECT id, username, password_hash FROM admin_users WHERE username = :username"),
                {"username": "admin"}
            )
            admin_data = result.fetchone()
            
            if admin_data:
                # 更新密码
                await session.execute(
                    text("UPDATE admin_users SET password_hash = :password_hash WHERE username = :username"),
                    {
                        "password_hash": get_password_hash(new_password),
                        "username": "admin"
                    }
                )
                await session.commit()
                print(f"✅ Admin password reset from {ADMIN_PASSWORD_ENV}")
            else:
                print("❌ Admin user not found")
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_admin())

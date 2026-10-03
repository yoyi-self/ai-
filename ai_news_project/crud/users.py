from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User, UserToken
from schemas.users import UserRequest, UpdateData
from utils.security import hash_password,verify_password

# token 有效期（天）
TOKEN_EXPIRE_DAYS = 7


#查询同户名是否存在
async def create_user_select(db: AsyncSession, username:str):
    stmt = select(User).where(User.username == username)
    user = await db.execute(stmt)
    return user.scalar_one_or_none()

#创建新用户
async def create_user(db: AsyncSession, User_data:UserRequest):
    hashed_pwd = hash_password(User_data.password)
    user = User(username=User_data.username,password=hashed_pwd)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

#创建更新token
async def create_user_token(db: AsyncSession, user_id: int) -> str:
    token_value = uuid4().hex
    expires_at = datetime.now() + timedelta(days=TOKEN_EXPIRE_DAYS)
    # 先查询用户是否已有 token，存在则更新，否则新建
    stmt = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.token = token_value
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token_value, expires_at=expires_at)
        db.add(user_token)
    await db.commit()
    return token_value

#查询验证用户是否存在
async def verify_user(db: AsyncSession, username: str,password:str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

#验证token并返回对应用户信息
async def verify_token(db: AsyncSession, token: str):
    stmt = select(UserToken).where(UserToken.token == token)
    result = await db.execute(stmt)
    user_token = result.scalar_one_or_none()
    if not user_token or datetime.now() > user_token.expires_at:
        return None
    user = select(User).where(User.id == user_token.user_id)
    result = await db.execute(user)
    return result.scalar_one_or_none()

#更新用户信息
async def update_user(db: AsyncSession, user_id: int, update_data: UpdateData):
    query = update(User).where(User.id == user_id).values(update_data.model_dump(exclude_none=True,exclude_unset=True))
    await db.execute(query)
    await db.commit()
    user = await db.get(User, user_id)
    if not user:
        return None
    return user

#修改用户密码
async def update_user_password(db: AsyncSession, user, old_password: str, new_password: str):
    if not verify_password(old_password, user.password):
        return None
    hashed_pwd = hash_password(new_password)
    user.password = hashed_pwd
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True



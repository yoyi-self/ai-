from fastapi import Header
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.params import Depends
from config.db_conf import get_db
from crud.users import verify_token


async def get_current_user(
        authorization : str = Header(...,alias="Authorization"),
        db: AsyncSession = Depends(get_db),
):
    token = authorization.replace("Bearer ", "")
    user = await verify_token(db,token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的令牌或已过期的令牌")
    return user

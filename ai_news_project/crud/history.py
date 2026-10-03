from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News_list


#添加浏览历史记录
async def add_history_list(db:AsyncSession, user_id: int, news_id: int):
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    if not result.scalars().first():
        history = History(user_id=user_id, news_id=news_id)
        db.add(history)
        await db.commit()
        return  history
    stmt = result.scalars().first()
    stmt.view_time = func.now()
    await db.commit()
    await db.refresh(stmt)
    return stmt

#查询浏览历史记录
async def get_history_list(db:AsyncSession,user_id: int, page,page_size):
    query = select(func.count(History.id)).where(History.user_id == user_id)
    result = await db.execute(query)
    total = result.scalar()
    offset = (page-1) * page_size
    query =  select(News_list,History.view_time.label("view_time"), History.id.label("history_id")).join(History,History.news_id == News_list.id).where(History.user_id == user_id).order_by(History.view_time.desc()).offset(offset).limit(page_size)
    rows = await db.execute(query)
    return total,rows.all()

#删除浏览历史记录
async def delete_history_list(db:AsyncSession,news_id:int,user_id:int):
    query = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

#清除浏览历史记录
async def clear_history_list(db:AsyncSession,user_id:int):
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount or 0

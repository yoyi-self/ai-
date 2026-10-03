from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite import Favorite
from models.news import News_list


#查询收藏装态函数
async def is_news_favorite(db:AsyncSession,use_id:int,news_id:int):
    query = select(Favorite).where(Favorite.news_id == news_id,Favorite.user_id == use_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None

#添加收藏函数
async def add_news_favorite(db:AsyncSession,use_id:int,news_id:int):
    favorite = Favorite(news_id=news_id,user_id=use_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

#取消收藏函数
async def remove_news_favorite(db:AsyncSession,user_id:int,news_id:int):
    query = delete(Favorite).where(Favorite.news_id == news_id,Favorite.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

#查询收藏列表函数
#总量+收藏新闻列表
async def get_favorite_news_list(db:AsyncSession,user_id:int,page:int,page_size:int):
    query = select(func.count()).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    total = result.scalar()
    offset = (page-1) * page_size
    query =  select(Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id")).join(Favorite, News_list.id == Favorite.news_id).where(Favorite.user_id == user_id).offset(offset).limit(page_size)
    rows = await db.execute(query)
    return total, rows.all()


#清空收藏列表
async def clear_favorite_news_list(db:AsyncSession,user_id:int):
    query = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount or 0

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News_list


#创建新闻目录分类查询函数
async def get_categories(db:AsyncSession,skip: int = 0,limit: int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

#创建按分类id查询新闻页函数
async def get_news_list(db:AsyncSession,category_id,skip: int = 0,limit: int = 100):
    stmt = select(News_list).where(News_list.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

#查询新闻总量函数
async def get_news_count(db:AsyncSession,category_id,):
    stmt = select(func.count(News_list.id)).where(News_list.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

#查询新闻详情函数
async def get_news_detail(db:AsyncSession,news_id:int):
    stmt = select(News_list).where(News_list.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

#新闻浏览量增加函数
async def increase_news_views(db:AsyncSession,category_id:int):
    stmt = (update(News_list).where(News_list.category_id == category_id).values(views=News_list.views + 1))
    await db.execute(stmt)

#查询返回相关新闻函数
async def get_related_news(db:AsyncSession,news_id:int,category_id:int,limit: int = 5):
    stmt = select(News_list).where(News_list.category_id == category_id,News_list.id != news_id).limit(limit)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    return [{
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "image": news.image,
        "author": news.author,
        "publishTime": news.publish_time,
        "categoryId": news.category_id,
        "views": news.views,
    } for news in related_news]

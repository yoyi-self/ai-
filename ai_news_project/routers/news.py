from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import alias
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query

from config.db_conf import get_db
from crud import news


#创建api router实例
router = APIRouter(prefix="/api/news", tags=["news"])

#新闻分类模块化路由
@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100,db:AsyncSession = Depends(get_db)):
    result = await news.get_categories(db,skip,limit)
    return {"code": 200,
            "message": "Success",
            "data":result}

#新闻列表模块化路由
@router.get("/list")
async def get_news_list(category_id : int = Query(...,alias="categoryId"),
                   page: int = 1,
                   page_size: int = Query(10,le = 100,alias="pageSize"),
                   db:AsyncSession = Depends(get_db)):
    offset = (page-1) * page_size
    result = await news.get_news_list(db,category_id,offset,page_size)
    total = await news.get_news_count(db,category_id)
    has_more = (offset + page_size) < total

    return {
        "code": 200,
        "message": "Success",
        "data":{
            "list":result,
            "total":total,
            "hasMore": has_more
        }
    }

#新闻详情模块化路由
@router.get("/detail")
async def get_news_detail(news_id:int = Query(...,alias="id"),db:AsyncSession = Depends(get_db)):
    result = await news.get_news_detail(db,news_id)
    if not result:
        raise HTTPException(status_code=404,detail="查找的新闻不存在")

    await news.increase_news_views(db,result.id)
    related_news_list = await news.get_related_news(db,result.id,result.category_id)
    return {
          "code": 200,
          "message": "success",
          "data": {
          "id": result.id,
          "title":result.title,
          "content": result.content,
          "image": result.image,
          "author": result.author,
          "publishTime": result.publish_time,
          "categoryId": result.category_id,
          "views": result.views,
          "relatedNews": related_news_list
  }
}

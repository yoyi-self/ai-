from fastapi import APIRouter, Depends, Query, HTTPException

from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from crud.favorite import is_news_favorite, add_news_favorite, remove_news_favorite, get_favorite_news_list, \
    clear_favorite_news_list
from models.users import User
from schemas.favorite import FavoriteCheckRequest, FavoriteAddRequest, FavoriteListRequest
from utils.auth import get_current_user

from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

#查询修改收藏状态路由
@router.get('/check')
async def check_favorite(news_id: int = Query(..., alias='newsId'),db:AsyncSession = Depends(get_db),user: User = Depends(get_current_user)):
    is_favorited = await is_news_favorite(db, user.id, news_id)

    return success_response(message="检查收藏状态成功", data=FavoriteCheckRequest(isFavorite=is_favorited))

#添加收藏
@router.post("/add")
async def add_favorite(data: FavoriteAddRequest,db:AsyncSession = Depends(get_db),user: User = Depends(get_current_user)):
    await add_news_favorite(db, user.id, data.news_id)
    return success_response(message="添加收藏成功",data=FavoriteCheckRequest(isFavorite=True))

#取消收藏
@router.delete("/remove")
async def remove_favorite(news_id:int = Query(..., alias='newsId'),user: User = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    if not await remove_news_favorite(db, user.id, news_id):
        raise HTTPException(status_code=404, detail="收藏记录不存在")
    return success_response(message="取消收藏成功")

#查询收藏列表
@router.get("/list")
async def get_favorite_list(page: int = Query(1,ge = 1),
                            page_size: int = Query(10,ge = 1,le = 100,alias = "pageSize"),
                            db:AsyncSession = Depends(get_db),user: User = Depends(get_current_user)):
    total,rows = await get_favorite_news_list(db, user.id, page, page_size)
    favorite_list = [
        {
            **news.__dict__,
            "favorite_time": favorite_time,
            "favorite_id": favorite_id
        }for news,favorite_id,favorite_time in rows
    ]
    has_more = total > page * page_size
    data = FavoriteListRequest(list = favorite_list, total = total, hasMore = has_more)
    return success_response(message="获取收藏列表成功",data=data)

#清空收藏列表
@router.delete("/clear")

async def clear_favorite(db:AsyncSession = Depends(get_db),user: User = Depends(get_current_user)):
    rows = await clear_favorite_news_list(db, user.id)
    return success_response(message=f"清空了{rows}条收藏")

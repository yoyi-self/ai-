from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.history import add_history_list, get_history_list, delete_history_list, clear_history_list
from models.users import User
from schemas.history import HistoryAddRequest, HistoryAddResponse, HistoryListRequest, HistoryNewsListRequest
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])



#添加浏览历史路由
@router.post('/add')
async def add_history(data: HistoryAddRequest,db:AsyncSession = Depends(get_db),user: User = Depends(get_current_user)):
    history = await add_history_list(db, user.id, data.news_id)

    return success_response(message="添加浏览历史成功", data=HistoryAddResponse(
        historyId=history.id,
        newsId=history.news_id,
        viewTime=history.view_time,
    ))

#查看浏览历史路由
@router.get('/list')
async def get_history(page:int = Query(1, ge=1), page_size:int = Query(10, ge=1), db:AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    total,rows = await get_history_list(db, user.id, page, page_size)
    history_list = [HistoryNewsListRequest.model_validate({
        **news.__dict__,
        "history_id": history_id,
        "view_time": view_time
    })for news,view_time,history_id in rows]
    has_more = total > page * page_size
    data = HistoryListRequest(list=history_list,total=total,hasMore=has_more)
    return success_response(message="获取浏览历史成功", data=data)

#删除浏览历史
@router.delete('/delete')
async def remove_history(news_id:int = Query(..., alias='newsId'),db:AsyncSession = Depends(get_db),user: User = Depends(get_current_user)):
    if not await delete_history_list(db, news_id, user.id):
        raise HTTPException(status_code=404, detail="浏览历史不存在")
    return success_response(message="删除浏览历史成功")

#清楚浏览历史
@router.delete('/clear')
async def clear_history(db:AsyncSession = Depends(get_db),user: User = Depends(get_current_user)):
    rows = await clear_history_list(db, user.id)
    return success_response(message=f"清除了{rows}条浏览记录")

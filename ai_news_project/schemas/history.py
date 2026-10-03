from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from schemas.base import NewsItemBase



class HistoryAddRequest(BaseModel):
    news_id : int = Field(...,alias="newsId")

class HistoryAddResponse(BaseModel):
    """添加浏览历史后的返回数据（History 为 ORM 对象，不能直接被 success_response 序列化）"""
    history_id: int = Field(..., alias="historyId")
    news_id: int = Field(..., alias="newsId")
    view_time: datetime = Field(..., alias="viewTime")
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class HistoryNewsListRequest(NewsItemBase):
    history_id: int = Field(..., alias="historyId")
    view_time: datetime = Field(..., alias="viewTime")
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)

class HistoryListRequest(BaseModel):
    list : list[HistoryNewsListRequest]
    total : int
    has_more : bool = Field(...,alias="hasMore")
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)


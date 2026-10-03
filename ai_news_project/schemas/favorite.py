from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)
    is_favorite : bool = Field(...,alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)
    news_id : int = Field(...,alias="newsId")

class FavoriteNewsListRequest(NewsItemBase):
    favorite_id: int = Field(..., alias="favoriteId")
    favorite_time: str = Field(..., alias="favoriteTime")


class FavoriteListRequest(BaseModel):
    list : list[FavoriteNewsListRequest]
    total : int
    has_more : bool = Field(...,alias="hasMore")
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)


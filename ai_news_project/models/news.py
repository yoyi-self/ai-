from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, String, Index, Text, ForeignKey,func
from sqlalchemy.orm import DeclarativeBase, Mapped,mapped_column

#创建基础类
class Base(DeclarativeBase):
    created_at : Mapped[datetime] = mapped_column(
        DateTime,insert_default=datetime.now(),comment="创建时间")
    updated_at : Mapped[datetime] = mapped_column(
        DateTime,insert_default=datetime.now(),onupdate=datetime.now(),comment="更新时间")

#创建新闻目录分类模型类
class Category(Base):
    __tablename__ = "news_category"
    id : Mapped[int] = mapped_column(Integer,primary_key=True,comment="目录分类id")
    name : Mapped[str] = mapped_column(String(50),unique=True,nullable=False,comment="目录分类名")
    sort_order : Mapped[int] = mapped_column(Integer,unique=True,nullable=False,comment="目录分类序号")

    def __repr__(self):
        return f"Category(id={self.id} name={self.name} sort_order={self.sort_order})"

#创建新闻列表模型类
class News_list(Base):
    __tablename__ = "news"

    __table_args__ = (
        Index("fx_news_category_idx", "category_id"),#高频查询场景
        Index("idx_publish_time", "publish_time"),#按发布时间排序场景
    )
    id : Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True,comment='新闻ID',)
    title : Mapped[str] = mapped_column(String(255),nullable=False,comment='新闻标题',)
    description : Mapped[Optional[str]] = mapped_column(String(500),nullable=True,comment='新闻简介',)
    content : Mapped[str] = mapped_column(Text,nullable=False,comment='新闻内容',)
    image : Mapped[Optional[str]] = mapped_column(String(255),nullable=True,comment='封面图片URL',)
    author : Mapped[Optional[str]] = mapped_column(String(50),nullable=True, comment='作者',)
    category_id : Mapped[int] = mapped_column(Integer,ForeignKey('news_category.id'), nullable=False,comment='分类ID',)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0',comment='浏览量')
    publish_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(),comment='发布时间')

    def __repr__(self):
        return f"<News(id={self.id},title={self.title},views={self.views})>"
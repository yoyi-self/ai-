from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

#创建引擎
async_engine = create_async_engine("mysql+aiomysql://root:tian040308@localhost/news_app?charset=utf8mb4",
                                   echo=True,
                                   pool_size=10,
                                   max_overflow=20)

#创建会话类
AsyncSessionLocal = async_sessionmaker(bind = async_engine,
                                       class_ = AsyncSession,
                                       expire_on_commit = False)

#创建depends依赖项
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise



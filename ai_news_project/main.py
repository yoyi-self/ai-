from fastapi import FastAPI
from routers import news, users, favorite, history
from  fastapi.middleware.cors import CORSMiddleware

from utils.exception_handler import register_exception_handlers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#允许的源
    allow_credentials=True,#允许携带cookie
    allow_methods=["*"],#允许的请求方法
    allow_headers=["*"],#允许的请求头
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

#注册全局异常处理器
register_exception_handlers(app)
#注册新闻分类目录模块化路由
app.include_router(news.router)
#注册用户模块化路由
app.include_router(users.router)
#注册收藏模块化路由
app.include_router(favorite.router)
#注册浏览历史模块化路由
app.include_router(history.router)







# if __name__ == '__main__':
#     print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

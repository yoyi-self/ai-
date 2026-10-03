from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.users import create_user_select, create_user, create_user_token, verify_user, update_user, update_user_password, update_user_password
from models.users import User
from schemas.users import UserRequest, UserInfo, RegisterData, UpdateData, ChangePassword
from utils.auth import get_current_user
from utils.response import success_response


router = APIRouter(prefix="/api/user",tags=["users"])

@router.post("/register")
async def register(user_data:UserRequest,db:AsyncSession = Depends(get_db)):
    # 注册逻辑：1.验证用户是否存在；2.创建用户；3.生成token；4.返回响应
    result = await create_user_select(db, user_data.username)
    if result:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")
    user_created = await create_user(db,user_data)
    token = await create_user_token(db, user_created.id)
    # user_info 接收 ORM 对象，由 UserInfo 序列化
    data = RegisterData(token=token, user_info=UserInfo.model_validate(user_created))
    return success_response("注册成功", data)

@router.post("/login")
async def login(user_data:UserRequest,db:AsyncSession = Depends(get_db)):
    #登录逻辑：1.验证用户是否存在；2.验证密码是否正确；3.生成token；4.返回响应
    user = await verify_user(db, user_data.username,user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await create_user_token(db, user.id)
    data = RegisterData(token=token, user_info=UserInfo.model_validate(user))
    return success_response("登录成功", data)

#查询用户信息
@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response("查询成功",data=UserInfo.model_validate(user))

#更新用户信息
@router.put("/update")
async def update_user_info(user_data: UpdateData, user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    user_updated = await update_user(db, user.id, user_data)
    return success_response("更新成功", data=UserInfo.model_validate(user_updated))

#修改用户密码
@router.put("/password")
async def change_password(userpwd: ChangePassword, user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    user_updated = await update_user_password(db, user, userpwd.old_password, userpwd.new_password)
    if not user_updated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码输入错误")
    return success_response("修改成功")

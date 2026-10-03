from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    """
    用户信息响应模型
    from_attributes=True 支持直接接收 ORM 对象并通过 model_validate 序列化
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    bio: Optional[str] = None
    avatar: Optional[str] = None


class RegisterData(BaseModel):
    """
    注册成功响应的 data 模型
    user_info 可接收 User ORM 对象（借助 UserInfo 的 from_attributes）
    """
    model_config = ConfigDict(from_attributes=True)

    token: str
    user_info: UserInfo

class UpdateData(BaseModel):
    """
    更新用户信息响应的 data 模型
    """
    nickname: str = None
    avatar: str = None
    gender : str = None
    bio: str = None
    phone : str = None

class ChangePassword(BaseModel):
    """
    修改用户密码响应的 data 模型
    """

    old_password: str = Field(...,alias="oldPassword",description="旧密码")
    new_password: str = Field(...,alias="newPassword",description="新密码")

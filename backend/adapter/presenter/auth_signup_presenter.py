from typing import Dict, Any
from usecase.auth_signup import CreateUserPresenter
from domain.entities.user import User


class CreateUserPresenterImpl(CreateUserPresenter):
    def output(self, user: User) -> Dict[str, Any]:
        """
        UserドメインオブジェクトをJSONシリアライズ可能な辞書に変換して返す。
        """
        return {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
        }


def new_auth_signup_presenter() -> CreateUserPresenter:
    """
    CreateUserPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return CreateUserPresenterImpl()
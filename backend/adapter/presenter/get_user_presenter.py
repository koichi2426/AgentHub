from typing import Dict, Any
from usecase.get_user import GetUserPresenter
from domain.entities.user import User


class GetUserPresenterImpl(GetUserPresenter):
    def output(self, user: User) -> Dict[str, Any]:
        """
        UserドメインオブジェクトをJSONシリアライズ可能な辞書に変換して返す。
        パスワードなどの機密情報は含めない。
        """
        return {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
        }


def new_get_user_presenter() -> GetUserPresenter:
    """
    GetUserPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetUserPresenterImpl()


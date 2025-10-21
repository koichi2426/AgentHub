from usecase.auth_login import LoginUserPresenter
from typing import Dict, Any


class LoginUserPresenterImpl(LoginUserPresenter):
    def output(self, token: str) -> Dict[str, Any]:
        """
        JWTトークンをJSONシリアライズ可能な辞書に変換して返す。
        """
        return {"token": token}


def new_login_user_presenter() -> LoginUserPresenter:
    """
    LoginUserPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return LoginUserPresenterImpl()
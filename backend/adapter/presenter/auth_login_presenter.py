from usecase.auth_login import LoginUserPresenter, LoginUserOutput
from typing import Dict, Any


class LoginUserPresenterImpl(LoginUserPresenter):
    def output(self, token: str) -> LoginUserOutput:
        """
        JWTトークンをLoginUserOutput DTOに変換して返す。
        """
        return LoginUserOutput(token=token)


def new_login_user_presenter() -> LoginUserPresenter:
    """
    LoginUserPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return LoginUserPresenterImpl()

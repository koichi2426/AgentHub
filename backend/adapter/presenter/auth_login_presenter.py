from usecase.auth_login import LoginUserPresenter, LoginUserOutput


class LoginUserPresenterImpl(LoginUserPresenter):
    def output(self, token: str) -> LoginUserOutput:
        """
        JWTトークンを LoginUserOutput DTO に変換して返す。
        """
        return LoginUserOutput(token=token)


def new_login_user_presenter() -> LoginUserPresenter:
    """
    LoginUserPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return LoginUserPresenterImpl()
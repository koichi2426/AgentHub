from usecase.get_user import GetUserPresenter, GetUserOutput
from domain.entities.user import User


class GetUserPresenterImpl(GetUserPresenter):
    def output(self, user: User) -> GetUserOutput:
        """
        Userドメインオブジェクトを GetUserOutput DTO に変換して返す。
        パスワードなどの機密情報は含めない。
        """
        return GetUserOutput(
            id=user.id.value,
            username=user.username,
            name=user.name,
            email=user.email.value,
            avatar_url=user.avatar_url,
        )


def new_get_user_presenter() -> GetUserPresenter:
    """
    GetUserPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetUserPresenterImpl()


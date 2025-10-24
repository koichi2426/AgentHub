from usecase.auth_signup import CreateUserPresenter, CreateUserOutput
from domain.entities.user import User


class CreateUserPresenterImpl(CreateUserPresenter):
    def output(self, user: User) -> CreateUserOutput:
        """
        Userドメインオブジェクトを CreateUserOutput DTO に変換して返す。
        """
        return CreateUserOutput(
            id=user.id.value,
            username=user.username,
            name=user.name,
            email=user.email.value,
            avatar_url=user.avatar_url,
        )


def new_auth_signup_presenter() -> CreateUserPresenter:
    """
    CreateUserPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return CreateUserPresenterImpl()

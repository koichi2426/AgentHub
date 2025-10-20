from usecase.auth_signup import CreateUserPresenter, CreateUserOutput, UserOutputDTO
from domain.entities.user import User


class CreateUserPresenterImpl(CreateUserPresenter):
    def output(self, user: User) -> CreateUserOutput:
        """
        User ドメインオブジェクトを CreateUserOutput に変換して返す。
        """
        dto = UserOutputDTO(
            id=getattr(user, "id", 0),
            username=getattr(user, "username", "") or getattr(user, "name", ""),
            name=getattr(user, "name", ""),
            email=getattr(user, "email", ""),
            avatar_url=getattr(user, "avatar_url", ""),
        )
        return CreateUserOutput(user=dto)


def new_auth_signup_presenter() -> CreateUserPresenter:
    """
    CreateUserPresenterImpl のファクトリ。
    """
    return CreateUserPresenterImpl()
import abc
from typing import List

# ユースケース層の依存関係
from usecase.get_image_stream import GetImageStreamPresenter, GetImageStreamOutput
# Output DTOをそのまま返すため、他のドメインエンティティは不要


class GetImageStreamPresenterImpl(GetImageStreamPresenter):
    def output(self, output_dto: GetImageStreamOutput) -> GetImageStreamOutput:
        """
        GetImageStreamOutput DTO をそのまま返す（パススルー）。
        ストリーミングデータはJSON変換の必要がないため。
        """
        # 変換ロジックは不要。そのまま次の層（コントローラ）に渡す。
        return output_dto


def new_get_image_stream_presenter() -> GetImageStreamPresenter:
    """
    GetImageStreamPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetImageStreamPresenterImpl()

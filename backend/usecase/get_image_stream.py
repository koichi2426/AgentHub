import os
import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Any

# ドメイン層の依存関係
from domain.value_objects.binary_stream import BinaryStream 
from domain.services.get_image_stream_domain_service import FileStreamDomainService 


# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetImageStreamUseCase(Protocol):
    """特定のパスの画像データをストリームとして取得するユースケースのインターフェース"""
    def execute(
        self, input: "GetImageStreamInput"
    ) -> Tuple["GetImageStreamOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput DTO
# ======================================
@dataclass
class GetImageStreamInput:
    """FastAPIから渡される、VPSの可視化ベースディレクトリに対する相対パス"""
    relative_path: str


# ======================================
# Output DTO
# ======================================
@dataclass
class GetImageStreamOutput:
    """取得した画像ストリームとそのメタデータ"""
    stream: BinaryStream
    mime_type: str
    filename: str


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetImageStreamPresenter(abc.ABC):
    """Output DTOをそのまま返すPresenterの抽象インターフェース"""
    @abc.abstractmethod
    def output(self, output_dto: GetImageStreamOutput) -> GetImageStreamOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetImageStreamInteractor:
    def __init__(
        self,
        presenter: "GetImageStreamPresenter",
        file_stream_service: FileStreamDomainService, 
    ):
        """依存性注入: PresenterとFileStreamDomainServiceを受け取る"""
        self.presenter = presenter
        self.file_stream_service = file_stream_service

    def execute(
        self, input: GetImageStreamInput
    ) -> Tuple["GetImageStreamOutput", Exception | None]:
        
        empty_output = GetImageStreamOutput(stream=None, mime_type="", filename="")
        
        try:
            # 1. ドメインサービスに画像ストリームの取得を委譲
            stream, mime_type = self.file_stream_service.get_file_stream_by_path(
                input.relative_path
            )

            # 2. ファイル名を取得
            filename = os.path.basename(input.relative_path)

            # 3. Output DTOを生成
            output = GetImageStreamOutput(
                stream=stream,
                mime_type=mime_type,
                filename=filename
            )

            # 4. Presenterに渡す (パススルーを想定)
            final_output = self.presenter.output(output)
            return final_output, None
            
        except Exception as e:
            # ファイルが見つからない、SFTP接続エラーなど
            return empty_output, e
        
# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_image_stream_interactor(
    presenter: "GetImageStreamPresenter",
    file_stream_service: FileStreamDomainService,
) -> "GetImageStreamUseCase":
    return GetImageStreamInteractor(
        presenter=presenter,
        file_stream_service=file_stream_service,
    )
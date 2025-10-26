from typing import Dict, Union, Any, List
from fastapi.responses import StreamingResponse, JSONResponse
import os

# ユースケース層の依存関係
from usecase.get_image_stream import (
    GetImageStreamUseCase,
    GetImageStreamInput,
    GetImageStreamOutput,
)


class GetImageStreamController:
    """
    画像ストリーム取得リクエストを処理し、ユースケースに委譲するコントローラ。
    Output DTO から StreamingResponse を構築する責務を持つ。
    """
    def __init__(self, uc: GetImageStreamUseCase):
        """依存性注入によりユースケースインスタンスを受け取る。"""
        self.uc = uc

    def execute(
        self, relative_path: str
    ) -> Union[StreamingResponse, JSONResponse]:
        """
        リクエストデータ（相対パス）をユースケースに渡し、StreamingResponseを生成して返す。
        
        Args:
            relative_path: VPSの可視化ベースディレクトリに対する相対パス。
            
        Returns:
            Union[StreamingResponse, JSONResponse]: 成功時は StreamingResponse、失敗時は JSONResponse。
        """
        # 1. Input DTOの生成
        input_data = GetImageStreamInput(relative_path=relative_path)
        
        try:
            # 2. ユースケースの実行
            output: GetImageStreamOutput
            err: Exception | None
            
            output, err = self.uc.execute(input_data)
            
            if err:
                # 3. エラー処理 (404/500)
                status_code = 500
                err_str = str(err).lower()
                
                # ファイルが見つからないエラーや、SFTP接続エラーを404として扱う
                if "not found" in err_str or "filestreamerror" in err_str:
                    status_code = 404
                
                # JSONResponseを返す
                return JSONResponse({"error": str(err)}, status_code=status_code)
            
            # 4. 成功レスポンス (StreamingResponseの構築)
            # Output DTOのstream (BinaryStream/BytesIO) を直接渡す。
            # stream は close() メソッドを持っているため、StreamingResponse が自動で閉じます。
            
            # 念のためストリームポインタを先頭に戻す
            if output.stream:
                output.stream.seek(0)
            else:
                 # streamがNoneの場合は404
                 return JSONResponse({"error": "Image stream is empty or null."}, status_code=404)

            return StreamingResponse(
                output.stream,
                media_type=output.mime_type,
                headers={
                    # ブラウザで画像をインライン表示させる
                    "Content-Disposition": f"inline; filename={output.filename}"
                }
            )
            
        except Exception as e:
            # 5. 予期せぬサーバーエラー処理 (500 Internal Server Error)
            return JSONResponse({"error": f"An unexpected server error occurred: {e}"}, status_code=500)
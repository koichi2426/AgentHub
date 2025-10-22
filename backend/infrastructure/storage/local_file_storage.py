import os
import shutil
from pathlib import Path
from fastapi import UploadFile

# ファイル保存のベースディレクトリを定義
# このパスは、docker-compose.yml でホストと共有されているディレクトリと一致する必要があります。
# 例: ホストの /mnt/training_data がコンテナ内の /data/training にマウントされている場合
# 環境変数で設定することが理想的ですが、ここではコンテナ内のマウントパスを仮定します。
STORAGE_BASE_DIR = "/data/training"

class FileStorageError(Exception):
    """ファイルストレージ操作に関するカスタムエラー"""
    pass

def initialize_storage():
    """ストレージディレクトリが存在することを確認し、なければ作成する"""
    path = Path(STORAGE_BASE_DIR)
    try:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"Storage directory created: {STORAGE_BASE_DIR}")
    except OSError as e:
        raise FileStorageError(f"Failed to initialize storage directory {STORAGE_BASE_DIR}: {e}")

def save_training_file(upload_file: UploadFile, agent_id: str) -> str:
    """
    アップロードされたファイルを共有ストレージに保存し、保存先パスを返す。

    Args:
        upload_file: FastAPIの UploadFile オブジェクト
        agent_id: ファイル名の一意性を確保するために使用するエージェントID (str)

    Returns:
        str: ファイルが保存された絶対パス（ワーカーが読み込むパス）
    
    Raises:
        FileStorageError: ファイル操作に失敗した場合
    """
    if not upload_file.filename:
        raise FileStorageError("File upload failed: filename is missing.")

    # ファイル名が一意になるようにIDとタイムスタンプを付加
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # パスとして安全なファイル名を生成
    safe_filename = Path(upload_file.filename).name
    
    # 最終的なコンテナ内の保存パス
    final_filename = f"{agent_id}_{timestamp}_{safe_filename}"
    file_path = Path(STORAGE_BASE_DIR) / final_filename
    
    # ファイル保存の実行
    try:
        # ディレクトリの存在確認 (コンテナ起動時に失敗している場合を考慮)
        initialize_storage() 

        with file_path.open("wb") as buffer:
            # UploadFileのコンテンツをストリームでファイルに書き込む
            shutil.copyfileobj(upload_file.file, buffer)
            
        # ワーカーがこのパスを使ってファイルを読み込む
        return str(file_path)

    except Exception as e:
        # ファイル保存中にエラーが発生した場合
        raise FileStorageError(f"Error saving file to {file_path}: {e}")


def delete_training_file(file_path: str) -> None:
    """
    指定されたパスのファイルを共有ストレージから削除する（クリーンアップ用）。
    """
    path = Path(file_path)
    try:
        if path.exists():
            path.unlink()
    except OSError as e:
        # 削除失敗はジョブ全体を妨げないが、ログに記録すべき
        print(f"Warning: Failed to delete file {file_path}. Error: {e}")

# 外部から datetime を使用するためにインポート
from datetime import datetime
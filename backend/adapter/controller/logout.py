"""
logout controller

エンドポイント: POST /logout

説明:
    - リクエストから現在のユーザーを特定し（cookie/jwt など）、
        セッションやトークンを無効化する処理を呼び出す。

実装メモ:
    - FastAPI の場合: `APIRouter` にルートを追加し、`Depends(get_current_user)` を使って現在ユーザーを取得
    - レスポンス: cookie をクリアするか、ステータス JSON を返す
    - ここはコメントのみ（実装しない）
"""

# POST /logout

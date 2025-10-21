import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class MySQLConfig:
    """
    MySQLデータベースへの接続情報を保持するデータクラス。
    """
    host: str
    port: int
    user: str
    password: str
    database: str

def NewMySQLConfigFromEnv() -> MySQLConfig:
    """
    .envファイルから環境変数を読み込み、MySQLConfigインスタンスを生成するファクトリ関数。

    プロジェクトのルートに、以下のような内容で.envファイルを作成してください:
    DB_HOST=db
    DB_PORT=3306
    DB_USER=root
    DB_PASSWORD=your_local_password
    DB_NAME=method_selector_db
    """
    load_dotenv()

    host = os.getenv("DB_HOST")
    port_str = os.getenv("DB_PORT")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    if not all([host, port_str, user, password, database]):
        raise ValueError(".envファイルに必要なデータベース設定がすべて含まれていません。")

    try:
        port = int(port_str)
    except ValueError:
        raise ValueError("DB_PORTは有効な整数である必要があります。")

    return MySQLConfig(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )
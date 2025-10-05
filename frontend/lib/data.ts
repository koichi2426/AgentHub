// エージェントオブジェクトの型定義 (簡素化版)
export type Agent = {
  id: string;
  name: string;
  owner: string;
  description: string;
  version: string;
};

// ユーザーオブジェクトの型定義 (変更なし)
export type User = {
  id: string;
  name: string;
  email: string;
  password_hash: string;
  avatar_url?: string;
};


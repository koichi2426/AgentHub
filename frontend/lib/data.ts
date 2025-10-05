// エージェントオブジェクトの型定義
export type Agent = {
  id: string;
  name: string;
  owner: string;
  description: string;
  version: string; // 最新バージョン
};

// ユーザーオブジェクトの型定義
export type User = {
  id: string;
  name: string;
  email: string;
  password_hash: string;
  avatar_url?: string;
};

// ファインチューニングジョブの型定義
export type FinetuningJob = {
  id: string;
  agentId: string;
  status: "completed" | "running" | "failed";
  createdAt: string;
  finishedAt?: string;
  modelId: string; // このジョブで生成されたモデルのID
};

// デプロイメント（API）の型定義
export type Deployment = {
  id:string;
  modelId: string;
  status: "active" | "inactive";
  endpoint: string;
  createdAt: string;
};


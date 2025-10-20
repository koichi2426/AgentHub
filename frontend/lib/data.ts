// エージェントオブジェクトの型定義
export type Agent = {
  id: string;
  name: string;
  owner: string;
  description: string;
};

// ユーザーオブジェクトの型定義
export type User = {
  id: string;
  name: string;
  email: string;
  password_hash: string;
  avatar_url: string;
};

// ファインチューニングジョブの型定義
export type FinetuningJob = {
  id: string;
  agentId: string;
  status: "completed" | "running" | "failed";
  createdAt: string;
  finishedAt?: string | null; // nullも許容
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

// 学習データへのリンク情報の型定義
export type TrainingLink = {
  jobId: string;
  dataUrl: string | null;
  fileName: string | null;
  recordCount: number | null;
  fileSize: string | null;
};

// 重み可視化データの重み部分の型定義
export type WeightVisualization = {
  name: string;
  before: string;
  after: string;
  delta: string;
};

// 重み可視化データのレイヤー部分の型定義
export type WeightLayer = {
  layerName: string;
  weights: WeightVisualization[];
};

// ジョブに紐づく重み可視化データ全体の型定義
export type Visualizations = {
  jobId: string;
  layers: WeightLayer[];
};
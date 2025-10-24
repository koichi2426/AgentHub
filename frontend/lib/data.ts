// frontend/lib/data.ts

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
// バックエンドの FinetuningJobListItem DTO (snake_case) に完全に合わせる
export type FinetuningJob = {
  id: string;
  agent_id: number;
  status: "completed" | "running" | "failed" | "queued";
  training_file_path: string; 
  error_message: string | null;
  created_at: string;
  finished_at: string | null; 
  model_id: string | null;
};

// デプロイメント（API）の型定義
export type Deployment = {
  id:string;
  model_id: string;
  status: "active" | "inactive";
  endpoint: string;
  created_at: string;
};

// 学習データへのリンク情報の型定義
export type TrainingLink = {
  job_id: string;
  data_url: string | null;
  file_name: string | null;
  record_count: number | null;
  file_size: string | null;
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
  layer_name: string;
  weights: WeightVisualization[];
};

// ジョブに紐づく重み可視化データ全体の型定義
export type Visualizations = {
  job_id: string;
  layers: WeightLayer[];
};
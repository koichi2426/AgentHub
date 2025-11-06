// frontend/lib/data.ts

// ======================================
// エージェントオブジェクトの型定義
// ======================================
export type Agent = {
  id: number;
  name: string;
  owner: string;
  description: string;
};

// ======================================
// ユーザーオブジェクトの型定義
// ======================================
export type User = {
  id: number;
  name: string;
  email: string;
  avatar_url: string;
};

// ======================================
// ファインチューニングジョブの型定義
// ======================================
export type FinetuningJob = {
  id: number;
  agent_id: number;
  status: "completed" | "running" | "failed" | "queued";
  training_file_path: string;
  error_message: string | null;
  created_at: string;
  finished_at: string | null;
};

// ======================================
// デプロイメント（API）の型定義
// ======================================
export type Deployment = {
  id: number;
  job_id: number;
  status: "active" | "inactive";
  endpoint: string;
};

// ======================================
// 学習データへのリンク情報の型定義
// ======================================
export type TrainingLink = {
  job_id: number;
  data_url: string | null;
  file_name: string | null;
  record_count: number | null;
  file_size: string | null;
};

// ======================================
// 重み可視化データの重み部分の型定義
// ======================================
export type WeightVisualizationDetail = {
  name: string;
  before_url: string;
  after_url: string;
  delta_url: string;
};

// ======================================
// 重み可視化データのレイヤー部分の型定義
// ======================================
export type WeightLayer = {
  layer_name: string;
  weights: WeightVisualizationDetail[];
};

// ======================================
// ジョブに紐づく重み可視化データ全体の型定義
// ======================================
export type Visualizations = {
  job_id: number;
  layers: WeightLayer[];
};

// ======================================
// デプロイメントメソッドのモックデータ型定義
// ======================================
export type DeploymentMethodsEntry = {
  deploymentId: number;
  methods: string[];
};

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

// ★★★ 修正箇所: 重み可視化データの重み部分の型定義 ★★★
// バックエンドの DTO (WeightVisualizationDetail) に合わせてプロパティ名を修正します
export type WeightVisualizationDetail = {
  name: string;
  before_url: string; // before -> before_url に修正
  after_url: string;   // after -> after_url に修正
  delta_url: string;   // delta -> delta_url に修正
};

// 重み可視化データのレイヤー部分の型定義
// ★★★ 修正箇所: 内部の型名を修正 ★★★
export type WeightLayer = {
  layer_name: string;
  weights: WeightVisualizationDetail[]; // WeightVisualization -> WeightVisualizationDetail に修正
};

// ジョブに紐づく重み可視化データ全体の型定義
// ★★★ 修正箇所: 内部の型名を修正 ★★★
export type Visualizations = {
  job_id: string;
  layers: WeightLayer[];
};

// ★★★ [新規追加] デプロイメントメソッドのモックデータ型定義 ★★★
export type DeploymentMethodsEntry = {
  deploymentId: string;
  methods: string[];
};
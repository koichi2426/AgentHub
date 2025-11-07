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
  created_at: string; // ISO 8601 string
  finished_at: string | null; // ISO 8601 string or null
};

// ★★★ 修正箇所: FinetuningJobListItem を FinetuningJob のエイリアスとしてエクスポート ★★★
export type FinetuningJobListItem = FinetuningJob; 
// ★★★ 修正箇所ここまで ★★★

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

// ======================================
// ★★★ 推論テスト結果の型定義 (新規追加) ★★★
// ======================================

interface EngineResponseRaw {
  results: Array<{ method: string; similarity: string }>;
  start_time_ns: string;
  end_time_ns: string;
}

interface PowerResponseRaw {
  status: string;
  gpu_index: number;
  power_watts: string;
  timestamp_ns: string;
}

/**
 * 個別ケースの結果 (InferenceCaseResult V.O. に対応)
 */
export type InferenceCaseResult = {
  id: number; // Presenterで付与される表示用ID
  input_data: string;
  expected_output: string;
  predicted_output: string;
  is_correct: boolean;
  raw_engine_response: EngineResponseRaw;
  raw_power_response: {
    base: PowerResponseRaw;
    active: PowerResponseRaw;
  };
};

/**
 * 全体の評価メトリクス (TestRunMetrics V.O. に対応)
 */
export type TestRunMetrics = {
  accuracy: number;
  latency_ms: number;
  cost_estimate_mwh: number;
  total_test_cases: number;
  correct_predictions: number;
};

/**
 * テスト結果のコンテナ (TestMetricsOutput DTO に対応)
 */
export type TestResultMetrics = {
  overall_metrics: TestRunMetrics;
  case_results: InferenceCaseResult[];
};

/**
 * Test Deployment Inference API の最終レスポンス型
 */
export type DeploymentTestResponse = {
  test_result: TestResultMetrics;
  message: string;
};

/**
 * メソッドリストのDTO (GetDeploymentMethodsResponse/SetDeploymentMethodsResponse の内部型)
 */
export type MethodListItemDTO = {
  name: string;
};
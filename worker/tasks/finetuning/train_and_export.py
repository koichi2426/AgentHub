#!/usr/bin/env python3
"""
train_and_export.py

ファインチューニング、ONNXエクスポート、INT8量子化、GGUFエクスポートを行うスクリプト。
ワーカーの実行環境で非対話的に使用される。
"""

from __future__ import annotations
import os
import argparse
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel
from onnxruntime.quantization import quantize_static, CalibrationDataReader, QuantType
import numpy as np
from tqdm import tqdm
import sys # 終了処理用
import subprocess # 🚨 GGUFエクスポートのために追加

# ==========================
# 共通設定 (引数で上書きされない限りこの値を使用)
# ==========================
MAX_LENGTH = 32
BATCH_SIZE = 16
EPOCHS = 3 # 実行時間を短縮するため、デフォルトを3に設定
LR = 2e-5
# Docker環境ではCUDAが利用可能か不明なため、CPUをデフォルトとし、CUDAがあれば使用
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TRAIN_DATA_DEFAULT = "data/train_triplets.txt"


# ==========================
# SBERT構造（mean pooling）
# ==========================
class SBERTEncoder(nn.Module):
    def __init__(self, bert_model):
        super().__init__()
        self.bert = bert_model

    def forward(self, input_ids, attention_mask):
        output = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden = output.last_hidden_state
        mask = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
        summed = (last_hidden * mask).sum(1)
        counts = mask.sum(1)
        mean_pooled = summed / counts
        return mean_pooled


# ==========================
# Tripletデータセット
# ==========================
class TripletDataset(Dataset):
    def __init__(self, path: str, tokenizer):
        self.samples = []
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) == 3:
                        self.samples.append(tuple(parts))
        except FileNotFoundError:
             print(f"ERROR: Training data file not found at {path}", file=sys.stderr)
             raise
        except Exception as e:
             print(f"ERROR: Failed to read training data: {e}", file=sys.stderr)
             raise

        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        a, p, n = self.samples[idx]
        return self.tokenizer(
            [a, p, n],
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=MAX_LENGTH
        )


# ==========================
# Triplet Loss
# ==========================
def triplet_loss(anchor, positive, negative, margin=1.0):
    d_ap = (anchor - positive).pow(2).sum(1)
    d_an = (anchor - negative).pow(2).sum(1)
    return torch.relu(d_ap - d_an + margin).mean()


# ==========================
# ファインチューニング処理
# ==========================
def finetune_model(model_name_or_path: str, training_file: str, output_dir: str, epochs: int, lr: float):
    print(f"\n[1] Loading model from {model_name_or_path} and tokenizer...")
    # トークナイザーとモデルをローカルパスから読み込み
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    base_model = AutoModel.from_pretrained(model_name_or_path)
    model = SBERTEncoder(base_model).to(DEVICE)

    dataset = TripletDataset(training_file, tokenizer)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

    print(f"[2] Starting fine-tuning (Epochs: {epochs}, LR: {lr})...")
    model.train()
    for epoch in range(epochs):
        losses = []
        for batch in tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}"):
            input_ids = batch["input_ids"].squeeze(1).to(DEVICE)
            attention_mask = batch["attention_mask"].squeeze(1).to(DEVICE)
            a, p, n = input_ids[:, 0, :], input_ids[:, 1, :], input_ids[:, 2, :]
            am, pm, nm = attention_mask[:, 0, :], attention_mask[:, 1, :], attention_mask[:, 2, :]
            va, vp, vn = model(a, am), model(p, pm), model(n, nm)
            loss = triplet_loss(va, vp, vn)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            losses.append(loss.item())

        print(f"  ✅ Epoch {epoch+1}/{epochs} Average Loss: {np.mean(losses):.4f}")

    print("\n✅ Fine-tuning complete.")

    # モデルを保存
    model.bert.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    torch.save(model.state_dict(), os.path.join(output_dir, "pytorch_model.bin"))
    print(f"✅ Model saved to {output_dir}")
    return tokenizer, model.bert # ONNXエクスポートのため、元のBERTモデルを返す


# ==========================
# ONNXエクスポート
# ==========================
def export_onnx(model, tokenizer, output_dir: str):
    print("\n[3] Exporting ONNX (FP32)...")
    model.eval()
    # output_dirに保存されることを想定
    onnx_fp32 = os.path.join(output_dir, "model_fp32.onnx")
    dummy_input_ids = torch.randint(0, tokenizer.vocab_size, (1, MAX_LENGTH), dtype=torch.long)
    dummy_attention_mask = torch.ones((1, MAX_LENGTH), dtype=torch.long)

    # ONNXエクスポートは元のBERTモデルで行う (SBERTEncoderではない)
    torch.onnx.export(
        model,
        (dummy_input_ids, dummy_attention_mask),
        onnx_fp32,
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"], # 埋め込みベクトル全体を出力
        dynamic_axes={"input_ids": {0: "batch"}, "attention_mask": {0: "batch"}},
        opset_version=13
    )
    print(f"✅ ONNX FP32 output complete → {onnx_fp32}")
    return onnx_fp32


# ==========================
# キャリブレーションデータ
# ==========================
class DummyCalibReader(CalibrationDataReader):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        # キャリブレーション用のダミーデータ（実際の訓練データからサンプリング推奨）
        self.datas = [
            tokenizer(
                "ファインチューニングの実行は正常に完了しました。",
                return_tensors="np",
                padding="max_length",
                truncation=True,
                max_length=MAX_LENGTH
            )
        ]
        self.index = 0

    def get_next(self):
        if self.index < len(self.datas):
            data = self.datas[self.index]
            self.index += 1
            return {
                "input_ids": data["input_ids"],
                "attention_mask": data["attention_mask"]
            }
        return None


# ==========================
# 量子化
# ==========================
def quantize_model(tokenizer, onnx_fp32: str, output_dir: str):
    print("\n[4] Executing INT8 quantization...")
    onnx_int8 = os.path.join(output_dir, "model_int8.onnx")
    quantize_static(
        model_input=onnx_fp32,
        model_output=onnx_int8,
        calibration_data_reader=DummyCalibReader(tokenizer),
        quant_format=QuantType.QUInt8
    )
    print(f"✅ INT8 quantization complete → {onnx_int8}")


# ==========================
# GGUFエクスポート (🚨 新規追加セクション)
# ==========================
def export_gguf(output_dir: str):
    print("\n[5] Exporting GGUF (for bert.cpp/llama.cpp)...")
    
    # GGUF変換スクリプト(convert-to-ggml.pyなど)のパスを環境変数から取得
    # Dockerfileで GGUF_CONVERT_SCRIPT=/app/bert.cpp/models/convert-to-ggml.py のように設定されていることを期待
    convert_script_path = os.environ.get("GGUF_CONVERT_SCRIPT")
    
    if not convert_script_path or not os.path.exists(convert_script_path):
        print(f"  ⚠️ WARNING: GGUF_CONVERT_SCRIPT environment variable not set or path invalid. Skipping GGUF export.")
        print(f"  (Path checked: {convert_script_path})")
        print("\n🎯 All training and ONNX export processes completed (GGUF skipped).")
        return # GGUF以外は成功として終了

    # bert.cpp/models/convert-to-ggml.py の命名規則に合わせる
    gguf_output_path = os.path.join(output_dir, f"ggml-model-f16.gguf") 
    
    # 🚨 修正: 変換コマンドの引数の順序をエラーログに基づき変更
    # 呼び出し形式: python convert-to-ggml.py <model_dir> <ftype_int> <output_file>
    # ftype_int: 0=f32, 1=f16 (と想定)
    cmd = [
        sys.executable,         # 現在のPythonインタープリタ
        convert_script_path,
        output_dir,             # sys.argv[1]: ファインチューニング済みモデルが保存されたディレクトリ
        "1",                    # sys.argv[2]: 出力タイプ (1 = f16 と想定)
        gguf_output_path        # sys.argv[3]: 出力ファイルパス
    ]
    
    print(f"  Running GGUF conversion command: {' '.join(cmd)}")
    
    try:
        # サブプロセスの標準出力とエラーをリアルタイムで表示しつつ実行
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(f"  [GGUF]: {line.strip()}", flush=True)
            process.stdout.close()
        
        return_code = process.wait()
        
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, cmd)
            
        print(f"✅ GGUF export complete → {gguf_output_path}")
        print("\n🎯 All training and export processes completed (including GGUF).")
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ ERROR: GGUF conversion failed with return code {e.returncode}.", file=sys.stderr)
        print("\n🎯 Training and ONNX export completed (GGUF FAILED).")
        # GGUF変換が失敗しても、ONNXは成功しているので、ここでは処理を停止しない
        
    except Exception as e:
        print(f"  ❌ ERROR: An unexpected error occurred during GGUF conversion: {e}", file=sys.stderr)
        print("\n🎯 Training and ONNX export completed (GGUF FAILED).")


# ==========================
# メイン処理 (非対話型)
# ==========================
def main():
    parser = argparse.ArgumentParser(description="Fine-tuning and model export script for TinyBERT models.")
    # 🚨 修正: .add.argument を .add_argument に修正
    parser.add_argument("--base_model_path", required=True, help="Local path to the base model directory (e.g., /app/worker/.../bert-tiny).")
    parser.add_argument("--training_file", required=True, help="Local path to the training data file (e.g., /tmp/job_ID/data/train_triplets.txt).")
    parser.add_argument("--output_dir", required=True, help="Directory to save the fine-tuned model and exports.")
    # 🚨 修正: 抜けていた --epochs と --lr の引数を追加
    parser.add_argument("--epochs", type=int, default=EPOCHS, help=f"Number of training epochs (default: {EPOCHS}).")
    parser.add_argument("--lr", type=float, default=LR, help=f"Learning rate (default: {LR}).")

    args = parser.parse_args()

    # --- 前処理 ---
    if not os.path.exists(args.training_file):
        raise FileNotFoundError(f"Training file not found: {args.training_file}")

    # 出力ディレクトリの作成
    os.makedirs(args.output_dir, exist_ok=True)

    # --- 訓練実行 ---
    tokenizer, model = finetune_model(
        model_name_or_path=args.base_model_path,
        training_file=args.training_file,
        output_dir=args.output_dir,
        epochs=args.epochs,
        lr=args.lr
    )

    # --- エクスポートと量子化 ---
    onnx_fp32 = export_onnx(model, tokenizer, args.output_dir)
    quantize_model(tokenizer, onnx_fp32, args.output_dir)

    # --- GGUFエクスポート (🚨 編集箇所) ---
    export_gguf(args.output_dir)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFATAL: Training pipeline failed: {e}", file=sys.stderr)
        sys.exit(1) # ワーカーに失敗を通知


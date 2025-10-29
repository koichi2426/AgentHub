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
import sys
import subprocess
import glob # GGUFのquantizeバイナリ検索のために追加

# ==========================
# 共通設定 (引数で上書きされない限りこの値を使用)
# ==========================
MAX_LENGTH = 32
BATCH_SIZE = 16
EPOCHS = 3
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
        # Mean Poolingの処理
        mask = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
        summed = (last_hidden * mask).sum(1)
        # ゼロ除算を避けるためにmin=1e-9を設定
        counts = torch.clamp(mask.sum(1), min=1e-9) 
        mean_pooled = summed / counts
        return mean_pooled


# ==========================
# Tripletデータセット
# ==========================
class TripletDataset(Dataset):
    # 修正: MAX_LENGTHを引数として受け取るように変更
    def __init__(self, path: str, tokenizer, max_length: int):
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
        self.max_length = max_length

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        a, p, n = self.samples[idx]
        return self.tokenizer(
            [a, p, n],
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=self.max_length # 修正: インスタンス変数を使用
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
# 修正: max_lengthを引数に追加
def finetune_model(model_name_or_path: str, training_file: str, output_dir: str, epochs: int, lr: float, max_length: int):
    print(f"\n[1] Loading model from {model_name_or_path} and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    base_model = AutoModel.from_pretrained(model_name_or_path)
    model = SBERTEncoder(base_model).to(DEVICE)

    # 修正: max_lengthを渡す
    dataset = TripletDataset(training_file, tokenizer, max_length) 
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    
    # ONNX INT8量子化のためのキャリブレーションデータを取得 (訓練ループの前に取得)
    calib_data_batch = next(iter(dataloader)) 

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
    # 修正: ONNXエクスポートのため、元のBERTモデルと、キャリブレーションデータバッチを返す
    return tokenizer, model.bert, calib_data_batch


# ==========================
# ONNXエクスポート
# ==========================
# 修正: max_lengthを引数に追加
def export_onnx(model, tokenizer, output_dir: str, max_length: int):
    print("\n[3] Exporting ONNX (FP32)...")
    model.eval()
    onnx_fp32 = os.path.join(output_dir, "model_fp32.onnx")
    # 修正: max_lengthを使用
    dummy_input_ids = torch.randint(0, tokenizer.vocab_size, (1, max_length), dtype=torch.long)
    dummy_attention_mask = torch.ones((1, max_length), dtype=torch.long)

    # ONNXエクスポートは元のBERTモデルで行う (SBERTEncoderではない)
    torch.onnx.export(
        model,
        (dummy_input_ids, dummy_attention_mask),
        onnx_fp32,
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"],
        dynamic_axes={"input_ids": {0: "batch"}, "attention_mask": {0: "batch"}},
        opset_version=14 # 修正済み
    )
    print(f"✅ ONNX FP32 output complete → {onnx_fp32}")
    return onnx_fp32


# ==========================
# キャリブレーションデータ
# ==========================
class CalibDataReaderFromBatch(CalibrationDataReader):
    # 修正: 実際の訓練データから取得したバッチを使用するクラス
    def __init__(self, calib_data_batch):
        # バッチから、最初のAnchor文の input_ids と attention_mask を抽出
        input_ids = calib_data_batch["input_ids"].squeeze(1)[:, 0, :]
        attention_mask = calib_data_batch["attention_mask"].squeeze(1)[:, 0, :]
        
        # NumPy配列に変換 (ONNX Runtimeの要求)
        self.input_ids = input_ids.numpy()
        self.attention_mask = attention_mask.numpy()
        self.index = 0

    def get_next(self):
        if self.index < len(self.input_ids):
            data = {
                # ONNX Runtimeが期待する形状 (1, max_length) にreshape
                "input_ids": self.input_ids[self.index].reshape(1, -1),
                "attention_mask": self.attention_mask[self.index].reshape(1, -1)
            }
            self.index += 1
            return data
        return None


# ==========================
# 量子化
# ==========================
# 修正: キャリブレーションデータバッチを受け取るように変更
def quantize_model(calib_data_batch, onnx_fp32: str, output_dir: str):
    print("\n[4] Executing INT8 quantization...")
    onnx_int8 = os.path.join(output_dir, "model_int8.onnx")
    
    # 修正: 実際のデータからCalibDataReaderを初期化
    calib_reader = CalibDataReaderFromBatch(calib_data_batch)
    
    quantize_static(
        model_input=onnx_fp32,
        model_output=onnx_int8,
        calibration_data_reader=calib_reader,
        quant_format=QuantType.QUInt8
    )
    print(f"✅ INT8 quantization complete → {onnx_int8}")


# ==========================
# GGUFエクスポート (llama.cpp対応に書き換え済み)
# ==========================
def export_gguf(output_dir: str):
    print("\n[5] Exporting GGUF (using llama.cpp conversion tools)...")
    
    # 1. パス解決: 環境変数またはフォールバックパスを使用
    # 環境変数から取得
    convert_script_path = os.environ.get("GGUF_CONVERT_SCRIPT")
    quantize_script_path = os.environ.get("GGUF_QUANTIZE_SCRIPT")

    # 🚨 修正: 環境変数で取得できなかった場合、フォールバックパスで上書きするロジック
    if not os.path.exists(convert_script_path) or not os.path.exists(quantize_script_path):
        LLAMA_CPP_BASE = "/app/llama.cpp"
        # 環境変数がない、またはパスが存在しない場合、既知のクローンパスを試す
        convert_script_path = os.path.join(LLAMA_CPP_BASE, "convert_hf_to_gguf.py")
        quantize_script_path = os.path.join(LLAMA_CPP_BASE, "build/bin/quantize") 

    
    if not os.path.exists(convert_script_path):
        print(f"  ❌ ERROR: Conversion script not found. Skipping GGUF export.")
        print(f"  (Checked path: {convert_script_path})")
        print("---")
        return

    # 1. F16 (Full Precision) への変換 (llama.cpp/convert-hf-to-gguf.pyを使用)
    gguf_f16_path = os.path.join(output_dir, "ggml-model-f16.gguf")
    
    # 呼び出し形式: python convert-hf-to-gguf.py <model_dir> --outfile <output_file> --outtype f16
    cmd_f16 = [
        sys.executable,
        convert_script_path,
        output_dir, 
        "--outfile", gguf_f16_path,
        "--outtype", "f16"
    ]
    
    print(f"  [5-1] Running F16 GGUF conversion: {' '.join(cmd_f16)}")
    
    try:
        # F16変換を実行
        # capture_output=Falseにして、リアルタイムで出力が見えるようにする (デバッグ用途)
        subprocess.run(cmd_f16, check=True, text=True, encoding='utf-8')
        print(f"  ✅ F16 GGUF export complete → {gguf_f16_path}")
        
    except subprocess.CalledProcessError as e:
        # エラーメッセージをログに出力
        stderr_output = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else e.stderr
        print(f"  ❌ ERROR: F16 GGUF conversion failed with return code {e.returncode}.", file=sys.stderr)
        print(f"  --- Stderr ---\n{stderr_output}", file=sys.stderr)
        print("---")
        return


    # 2. Q4_0 (4-bit quantization) への量子化 (llama.cpp/quantizeバイナリを使用)
    if not os.path.exists(quantize_script_path):
        print("  ⚠️ WARNING: GGUF quantize binary not found. Skipping 4-bit quantization.")
        print(f"  (Checked path: {quantize_script_path})")
        print("\n🎯 All training and export processes completed (GGUF Q4_0 skipped).")
        return
        
    gguf_q4_path = os.path.join(output_dir, "ggml-model-q4_0.gguf") 
    
    # 呼び出し形式: ./quantize <input.gguf> <output.gguf> <quant_type>
    cmd_q4 = [
        quantize_script_path,
        gguf_f16_path,          # 入力ファイル (F16モデル)
        gguf_q4_path,           # 出力ファイル (Q4_0モデル)
        "Q4_0"                  # 量子化タイプ
    ]
    
    print(f"  [5-2] Running Q4_0 quantization: {' '.join(cmd_q4)}")
    
    try:
        # Q4_0量子化を実行
        # capture_output=Falseにして、リアルタイムで出力が見えるようにする
        subprocess.run(cmd_q4, check=True, text=True, encoding='utf-8')
        print(f"  ✅ Q4_0 GGUF export complete → {gguf_q4_path}")
        
    except subprocess.CalledProcessError as e:
        # エラーメッセージをログに出力
        stderr_output = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else e.stderr
        print(f"  ❌ ERROR: Q4_0 GGUF quantization failed with return code {e.returncode}.", file=sys.stderr)
        print(f"  --- Stderr ---\n{stderr_output}", file=sys.stderr)
        print("\n🎯 Training and ONNX export completed (GGUF Q4_0 FAILED).")
        return
        
    print("\n🎯 All training and export processes completed (including GGUF).")


# ==========================
# メイン処理 (非対話型)
# ==========================
def main():
    parser = argparse.ArgumentParser(description="Fine-tuning and model export script for TinyBERT models.")
    # 修正: .add_argument に統一
    parser.add_argument("--base_model_path", required=True, help="Local path to the base model directory (e.g., /app/worker/.../bert-tiny).")
    parser.add_argument("--training_file", required=True, help="Local path to the training data file (e.g., /tmp/job_ID/data/train_triplets.txt).")
    parser.add_argument("--output_dir", required=True, help="Directory to save the fine-tuned model and exports.")
    # 修正: 抜けていた引数を追加
    parser.add_argument("--epochs", type=int, default=EPOCHS, help=f"Number of training epochs (default: {EPOCHS}).")
    parser.add_argument("--lr", type=float, default=LR, help=f"Learning rate (default: {LR}).")
    # 追加: MAX_LENGTHも引数で受け取れるようにする
    parser.add_argument("--max_length", type=int, default=MAX_LENGTH, help=f"Maximum sequence length (default: {MAX_LENGTH}).")

    args = parser.parse_args()

    # --- 前処理 ---
    if not os.path.exists(args.training_file):
        raise FileNotFoundError(f"Training file not found: {args.training_file}")

    # 出力ディレクトリの作成
    os.makedirs(args.output_dir, exist_ok=True)

    # --- 訓練実行 ---
    # 修正: max_lengthを渡し、calib_data_batchを受け取る
    tokenizer, model, calib_data_batch = finetune_model(
        model_name_or_path=args.base_model_path,
        training_file=args.training_file,
        output_dir=args.output_dir,
        epochs=args.epochs,
        lr=args.lr,
        max_length=args.max_length
    )

    # --- エクスポートと量子化 ---
    # 修正: max_lengthを渡す
    onnx_fp32 = export_onnx(model, tokenizer, args.output_dir, args.max_length)
    # 修正: キャリブレーションデータを渡す
    quantize_model(calib_data_batch, onnx_fp32, args.output_dir)

    # --- GGUFエクスポート (最終目的) ---
    export_gguf(args.output_dir)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        print(f"\nFATAL: Training pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)

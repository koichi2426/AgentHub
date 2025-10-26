#!/usr/bin/env python3
"""
visualize_finetuning_diff.py

ファインチューニングによる重み変化を可視化するスクリプト。
ワーカーの実行環境で非対話的に使用される。
"""

from __future__ import annotations
import argparse
import os
import re
import torch
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional # Optionalを追加
import sys

# matplotlibのバックエンド設定 (Docker環境でのエラー回避)
plt.switch_backend('Agg')

# safetensorsのチェック
try:
    from safetensors.torch import load_file as safe_load_file
    _HAVE_SAFETENSORS = True
except Exception:
    _HAVE_SAFETENSORS = False


# ===============================
# モデル重みロード
# ===============================
def _load_state_dict(path: str) -> dict[str, torch.Tensor]:
    """PyTorchまたはSafeTensorsファイルから重みをロード"""
    if not os.path.exists(path):
        # 実行権限エラーではなくファイルが見つからないことを示す
        raise FileNotFoundError(f"❌ モデルファイルが見つかりません: {path}")
    ext = os.path.splitext(path)[1].lower()
    
    # 訓練スクリプトが出力する 'pytorch_model.bin' を直接読み込む
    if ext == ".bin":
        sd = torch.load(path, map_location="cpu")
        return sd["state_dict"] if "state_dict" in sd else sd
    elif ext in (".safetensors", ".safe"):
        if not _HAVE_SAFETENSORS:
            raise RuntimeError("safetensors not installed. pip install safetensors")
        return safe_load_file(path, device="cpu")
    else:
        # ディレクトリパスが渡された場合、pytorch_model.binをチェック
        if os.path.isdir(path):
            bin_path = os.path.join(path, "pytorch_model.bin")
            if os.path.exists(bin_path):
                 return _load_state_dict(bin_path)
        raise ValueError(f"Unsupported file format or directory structure: {path}")


# ===============================
# 汎用描画関数（自動スケーリング対応）
# ===============================
def save_heatmap(name: str, arr: np.ndarray, outdir: str, cmap="bwr"):
    """ヒートマップを生成し、指定ディレクトリにPNGとして保存"""
    plt.figure(figsize=(6, 4))

    # 差分ヒートマップの場合、色範囲を中央値（0）で対称にする
    if "delta" in name.lower():
        # 99パーセンタイルでクリッピング
        vmax = np.percentile(np.abs(arr), 99) if len(arr.flat) > 0 else 1.0
        vmin = -vmax
        cmap = "bwr" 
    else:
        vmax = np.percentile(arr, 99) if len(arr.flat) > 0 else 1.0
        vmin = np.percentile(arr, 1) if len(arr.flat) > 0 else 0.0
        cmap = "viridis"

    plt.imshow(arr, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.title(name, fontsize=8)
    plt.tight_layout()

    # パスをサニタイズ
    # 注意: nameはPyTorchの重み名 (例: bert.encoder.layer.0.attention.self.key.weight_delta)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
    out = os.path.join(outdir, f"{safe_name}.png")
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(out), exist_ok=True) 
    
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"[heatmap] Saved {name} -> {out}")
    return out 


def plot_layer_deltas(deltas: list[float], outdir: str, title="Weight Change per Layer"):
    """L2ノルム変化プロット (現在は未使用だが、コードは残す)"""
    plt.figure(figsize=(6, 3))
    plt.plot(deltas, marker="o")
    plt.title(title)
    plt.xlabel("Layer Index")
    plt.ylabel("L2 Δ Weight")
    plt.tight_layout()
    out = os.path.join(outdir, "layer_deltas.png")
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"[plot] {title} -> {out}")


# ===============================
# メイン処理 (非対話型)
# ===============================
def main():
    parser = argparse.ArgumentParser(description="Visualize fine-tuning weight differences.")
    parser.add_argument("--base_model_path", required=True, help="Path to the base model directory (containing pytorch_model.bin).")
    parser.add_argument("--finetuned_model_path", required=True, help="Path to the fine-tuned model directory (containing pytorch_model.bin).")
    parser.add_argument("--output_dir", required=True, help="Directory to save the visualization PNG files.")

    args = parser.parse_args()

    # --- パスの設定と確認 ---
    pre_bin_path = os.path.join(args.base_model_path, "pytorch_model.bin")
    post_bin_path = os.path.join(args.finetuned_model_path, "pytorch_model.bin")

    if not os.path.exists(post_bin_path):
        raise FileNotFoundError(f"❌ ファインチューニング済みモデルが見つかりません: {post_bin_path}")
        
    # --- モデル読み込み ---
    sd_pre = _load_state_dict(pre_bin_path)
    sd_post = _load_state_dict(post_bin_path)

    # --- 出力ディレクトリの作成 ---
    os.makedirs(args.output_dir, exist_ok=True)
    
    delta_per_layer = []

    # --- 重み比較と可視化 ---
    for name, t_pre in sd_pre.items():
        if not isinstance(t_pre, torch.Tensor):
            continue
        # エンコーダーのレイヤー重みのみを対象とする
        if not re.search(r"encoder\.layer\.\d+\.", name):
            continue
        if name not in sd_post:
            continue
        
        t_post = sd_post[name]
        np_pre = t_pre.detach().cpu().numpy()
        np_post = t_post.detach().cpu().numpy()
        delta = np_post - np_pre

        # --- レイヤー別ディレクトリ作成 (サブディレクトリに保存) ---
        m = re.search(r"encoder\.layer\.(\d+)\.", name)
        layer_id = int(m.group(1)) if m else -1
        # 出力ディレクトリ/layerX/ に保存
        layer_dir = os.path.join(args.output_dir, f"layer{layer_id}")
        
        # --- 可視化と保存 ---
        # 重み名に含まれるドットをアンダースコアに変換し、ローカル相対パスを正しく構築する
        safe_name_base = name.replace('.', '_')
        
        # Query/Key/Value および Feed Forward 層の重みのみを可視化
        if re.search(r"(query|key|value|intermediate|output)\.dense\.weight", name):
            save_heatmap(safe_name_base + "_before", np_pre, layer_dir)
            save_heatmap(safe_name_base + "_after", np_post, layer_dir)
            save_heatmap(safe_name_base + "_delta", delta, layer_dir)
            
            # (L2ノルム変化の計算は残すが、プロットは行わない)
            delta_per_layer.append(np.linalg.norm(delta))

    # L2ノルム変化のプロットは、ワーカーの処理負荷軽減のため省略
    # if delta_per_layer:
    #     plot_layer_deltas(delta_per_layer, args.output_dir)

    print("\n🎯 All visualization processes completed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFATAL: Visualization failed: {e}", file=sys.stderr)
        sys.exit(1)

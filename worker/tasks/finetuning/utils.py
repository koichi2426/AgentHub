# worker/tasks/finetuning/utils.py

import os
import subprocess
import re
import json
from typing import Optional, List, Dict, Any

def parse_visualization_output(uploaded_image_paths: Dict[str, str], job_id: int) -> List[Dict[str, Any]]:
    """
    アップロードされた可視化画像パスの辞書をDB保存用の形式に変換。
    キー: ローカル相対パス (例: 'layer0/bert..._delta.png')
    値:   リモート絶対パス/URL (例: '/visualizations/job_123/layer0/bert..._delta.png')
    """
    layers_dict: Dict[str, Dict[str, Any]] = {}
    print(f"DEBUG: Parsing visualization paths for Job {job_id}: {uploaded_image_paths}")

    for local_rel_path, remote_url in uploaded_image_paths.items():
        parts = local_rel_path.split(os.sep)
        if len(parts) < 2:
            print(f"WARN: Job {job_id}: Skipping unexpected vis path: {local_rel_path}")
            continue

        layer_dir_name = parts[0] # e.g., 'layer0'
        file_name = parts[-1]     # e.g., 'bert...weight_delta.png'

        # ファイル名から重み名と種類を抽出
        match = re.match(r"(.*)_(before|after|delta)\.png", file_name)
        if not match:
            print(f"WARN: Job {job_id}: Cannot parse vis filename: {file_name}")
            continue

        weight_name_base = match.group(1).replace('_', '.') # Restore dots
        image_type = match.group(2) # 'before', 'after', 'delta'

        # 辞書構造を構築
        if layer_dir_name not in layers_dict:
            layers_dict[layer_dir_name] = {"layer_name": layer_dir_name, "weights": {}}

        if weight_name_base not in layers_dict[layer_dir_name]["weights"]:
            layers_dict[layer_dir_name]["weights"][weight_name_base] = {"name": weight_name_base}

        url_key = f"{image_type}_url" # 'before_url', 'after_url', 'delta_url'
        layers_dict[layer_dir_name]["weights"][weight_name_base][url_key] = remote_url

    # 最終的なリスト構造に変換
    final_layers_data = []
    # Sort layers by name (e.g., layer0, layer1, ...)
    for layer_name in sorted(layers_dict.keys()): 
        layer_data = layers_dict[layer_name]
        # Sort weights within a layer by name (optional but good for consistency)
        weights_list = sorted(
            list(layer_data.get("weights", {}).values()), 
            key=lambda w: w.get("name", "")
        )
        if weights_list: # Only add layers that had valid weight images
            final_layers_data.append({
                "layer_name": layer_name,
                "weights": weights_list
            })

    print(f"DEBUG: Job {job_id}: Parsed layers data: {json.dumps(final_layers_data, indent=2)}") # Debug output
    return final_layers_data

def run_script(job_id: int, script_path: str, args: List[str], cwd: str) -> bool:
    """外部Pythonスクリプトを実行し、成否を返す。失敗時はRuntimeErrorを送出。"""
    if not os.path.isfile(script_path):
        err_msg = f"Script not found: {script_path}"
        print(f"ERROR: Job {job_id}: {err_msg}")
        raise FileNotFoundError(err_msg)

    command = ["python", script_path] + args
    print(f"INFO: Job {job_id}: Executing: {' '.join(command)}")
    try:
        # Execute and wait, check=True raises CalledProcessError on non-zero exit
        process = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd)
        # Log output even on success for debugging/transparency
        print(f"--- Script STDOUT ---\n{process.stdout}\n---------------------")
        print(f"INFO: Job {job_id}: Script '{os.path.basename(script_path)}' executed successfully.")
        return True # Indicate success
    except subprocess.CalledProcessError as e:
        # Log error details extensively
        print(f"ERROR: Job {job_id}: Script '{os.path.basename(script_path)}' failed with exit code {e.returncode}!")
        print(f"--- Script STDERR ---\n{e.stderr}\n---------------------")
        print(f"--- Script STDOUT ---\n{e.stdout}\n---------------------")
        # Raise a runtime error including stderr content for the pipeline to catch
        stderr_excerpt = (e.stderr or "No stderr output.")[:500] # Limit length
        raise RuntimeError(f"Script {os.path.basename(script_path)} failed. Stderr: {stderr_excerpt}")
    except Exception as e:
        # Catch other potential errors during execution (e.g., permission issues)
        print(f"ERROR: Job {job_id}: Failed to run script '{os.path.basename(script_path)}': {e}")
        raise RuntimeError(f"Failed to execute script {os.path.basename(script_path)}: {e}") # Raise general runtime error

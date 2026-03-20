import pandas as pd
import subprocess
import os
import sys
import math

# --- 配置 ---
# 我们将自动使用你当前激活的 Conda 环境中的 Python
PYTHON_EXECUTABLE = sys.executable 
PREDICT_SCRIPT = "predict.py"
# 错误标识符 (从你的错误日志中复制)
ERROR_SIGNATURE = "Dimensions must be equal" 
# ---

def run_prediction(csv_path, num_molecules):
    """
    在子进程中运行 predict.py 并检查其输出。
    返回 "SUCCESS", "FAIL_DIMENSION_ERROR", 或 "FAIL_OTHER_ERROR"
    """
    command = [PYTHON_EXECUTABLE, PREDICT_SCRIPT, csv_path, str(num_molecules)]
    
    # 打印我们正在测试的命令
    # print(f"  > Testing: {' '.join(command)}")
    
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        print(f"  > Batch {csv_path} timed out. Assuming failure.")
        return "FAIL_OTHER_ERROR"

    stderr_output = process.stderr.lower()
    
    if ERROR_SIGNATURE.lower() in stderr_output:
        # 这是我们正在寻找的特定错误！
        return "FAIL_DIMENSION_ERROR"
    elif process.returncode != 0:
        # 发生了其他错误 (比如之前的 'input 6 not in allowable set')
        # print(f"  > Other Error: {process.stderr}")
        return "FAIL_OTHER_ERROR"
    else:
        # 一切正常
        return "SUCCESS"

def find_bad_molecules_recursive(molecule_df, prefix="root"):
    """
    使用递归二分搜索来查找坏分子。
    """
    num_mols = len(molecule_df)
    
    # --- 1. 创建此批次的临时CSV文件 ---
    current_csv_path = f"temp_batch_{prefix}.csv"
    molecule_df.to_csv(current_csv_path, index=False)
    
    # --- 2. 运行预测 ---
    print(f"Testing batch '{prefix}' with {num_mols} molecules...")
    status = run_prediction(current_csv_path, num_mols)
    
    # --- 3. 基本情况：如果只剩一个分子 ---
    if num_mols == 1:
        os.remove(current_csv_path) # 清理临时文件
        if status != "SUCCESS":
            print(f"!!! 找到一个坏分子: {molecule_df.iloc[0]['substance_id']}")
            return molecule_df # 返回这个坏分子
        else:
            return pd.DataFrame() # 这个分子是好的，返回空

    # --- 4. 递归步骤：如果超过一个分子 ---
    
    if status == "SUCCESS":
        # 整个批次都成功了，我们不需要再深入了
        print(f"  > Batch '{prefix}' ({num_mols} mols) 成功. 此分支无坏分子.")
        os.remove(current_csv_path) # 清理临时文件
        return pd.DataFrame() # 返回空
    
    elif status == "FAIL_DIMENSION_ERROR":
        # 批次失败了，我们必须深入
        print(f"  > Batch '{prefix}' ({num_mols} mols) 失败. 拆分...")
        
        midpoint = math.ceil(num_mols / 2)
        df_a = molecule_df.iloc[:midpoint]
        df_b = molecule_df.iloc[midpoint:]
        
        # 递归搜索两个子批次
        bad_ones_a = find_bad_molecules_recursive(df_a, f"{prefix}_A")
        bad_ones_b = find_bad_molecules_recursive(df_b, f"{prefix}_B")
        
        os.remove(current_csv_path) # 清理临时文件
        return pd.concat([bad_ones_a, bad_ones_b]) # 返回所有找到的坏分子

    else: # FAIL_OTHER_ERROR
        print(f"  > Batch '{prefix}' 遇到了一个意外错误 (不是维度错误).")
        print(f"  > 无法从此分支中定位坏分子。将跳过此分支。")
        os.remove(current_csv_path)
        return pd.DataFrame()

def main():
    if len(sys.argv) < 2:
        print("--- DeepChemStable 坏SMILES查找器 ---")
        print("用法: python find_bad_smiles.py <你的失败批次.csv>")
        print("\n例如: python find_bad_smiles.py my_5000_batch.csv")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"错误: 找不到文件 '{input_file}'")
        sys.exit(1)
        
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        sys.exit(1)
        
    print(f"--- 开始在 {input_file} (共 {len(df)} 个分子) 中搜索坏SMILES ---")
    
    final_bad_ones = find_bad_molecules_recursive(df, "root")
    
    if len(final_bad_ones) > 0:
        print("\n--- 搜索完成. 找到以下导致错误的分子: ---")
        print(final_bad_ones)
        
        output_filename = "found_bad_smiles.csv"
        final_bad_ones.to_csv(output_filename, index=False)
        print(f"\n已将列表保存到 '{output_filename}'")
    else:
        print("\n--- 搜索完成. 未找到导致维度错误的分子 ---")
        print("这很奇怪。请确保你提供的CSV文件确实会导致'Dimensions must be equal'错误。")

if __name__ == "__main__":
    main()
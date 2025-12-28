import os
import sys

# 將專案根目錄加入 Python 路徑，確保可以匯入 app 模組
sys.path.append(os.getcwd())

try:
    from app.graph.agents.consultant.agent import build_consultant_graph
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("請確保你在 'backend' 資料夾下執行此腳本: python mermaid.py")
    sys.exit(1)


def main():
    print("🎨 正在產生 Mermaid 圖表 (FSM/DAG)...")

    try:
        # 建構圖形
        app = build_consultant_graph()

        # 取得 Mermaid 語法
        mermaid_code = app.get_graph().draw_mermaid()

        # 輸出到檔案
        output_file = "graph_diagram.mmd"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(mermaid_code)

        print(f"✅ 成功！Mermaid 語法已儲存至: {output_file}")
        print("\n--- Mermaid Code (複製下方內容到 https://mermaid.live 檢視) ---\n")
        print(mermaid_code)
        print("\n------------------------------------------------------------\n")

    except Exception as e:
        print(f"❌ 產生失敗: {e}")


if __name__ == "__main__":
    main()

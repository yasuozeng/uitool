import asyncio
import sqlite3
from pathlib import Path

# 获取数据库路径
DB_PATH = Path(__file__).parent / "data" / "uitool.db"

def add_case_ids_column():
    """添加 case_ids_json 列到 executions 表"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # 检查列是否已存在
        cursor.execute("PRAGMA table_info(executions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'case_ids_json' not in columns:
            # 添加新列
            cursor.execute("""
                ALTER TABLE executions 
                ADD COLUMN case_ids_json TEXT
            """)
            conn.commit()
            print("[OK] Added case_ids_json column to executions table")
        else:
            print("[INFO] case_ids_json column already exists")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_case_ids_column()

import sqlite3
import sys

def delete_data(data_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        # 首先检查数据是否存在
        cursor.execute("SELECT * FROM comments WHERE id = ?", (data_id,))
        data = cursor.fetchone()
        
        if data is None:
            print(f"Data with id {data_id} does not exist.")
            return

        # 执行删除操作
        cursor.execute("DELETE FROM comments WHERE id = ?", (data_id,))
        conn.commit()
        
        print(f"Data with id {data_id} has been successfully deleted.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python deletedata.py <data_id>")
        sys.exit(1)
    
    try:
        data_id = int(sys.argv[1])
    except ValueError:
        print("Error: Data ID must be an integer.")
        sys.exit(1)

    delete_data(data_id)


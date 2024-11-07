from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允许跨域访问

DATABASE = 'database.db'

# 数据库初始化
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            image TEXT,
            author TEXT,
            date TEXT
        )''')

# 获取所有评论
@app.route('/comments', methods=['GET'])
def get_comments():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT * FROM comments ORDER BY id DESC')
        comments = [
            {"id": row[0], "text": row[1], "image": row[2], "author": row[3], "date": row[4]}
            for row in cursor.fetchall()
        ]
    return jsonify(comments)

# 添加新评论
@app.route('/comments', methods=['POST'])
def add_comment():
    data = request.json
    text = data.get('text', '')
    image = data.get('image', '')
    author = data.get('author', 'Anonymous User')
    date = datetime.now().isoformat()

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('INSERT INTO comments (text, image, author, date) VALUES (?, ?, ?, ?)',
                              (text, image, author, date))
        conn.commit()
        comment_id = cursor.lastrowid

    return jsonify({"id": comment_id, "text": text, "image": image, "author": author, "date": date})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=7805)

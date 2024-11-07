from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
from datetime import datetime
import logging
import json

app = Flask(__name__)
CORS(app, resources={r"/comments": {"origins": "*"}})

# 增加最大请求大小限制
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

DATABASE = 'database.db'

# 配置日志
logging.basicConfig(level=logging.DEBUG)  # 将日志级别改为 DEBUG
logger = logging.getLogger(__name__)

# 数据库初始化
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            images TEXT,
            author TEXT,
            date TEXT
        )''')
        # 添加索引以提高查询性能
        conn.execute('CREATE INDEX IF NOT EXISTS idx_date ON comments(date)')

# 获取数据库连接
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# 获取评论（带分页）
@app.route('/comments', methods=['GET'])
def get_comments():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit

        logger.debug(f"Fetching comments: page={page}, limit={limit}, offset={offset}")

        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM comments ORDER BY id DESC LIMIT ? OFFSET ?', (limit, offset))
            rows = cursor.fetchall()
            logger.debug(f"Fetched {len(rows)} rows from database")

            comments = []
            for row in rows:
                try:
                    images = json.loads(row[2]) if row[2] else []
                    comments.append({
                        "id": row[0],
                        "text": row[1],
                        "images": images,
                        "author": row[3],
                        "date": row[4]
                    })
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON for comment {row[0]}: {str(e)}")
                    # 跳过无效的评论，但不中断整个处理
                    continue

        logger.debug(f"Returning {len(comments)} comments")
        return jsonify(comments)
    except Exception as e:
        logger.error(f"Error getting comments: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# 添加新评论
@app.route('/comments', methods=['POST'])
def add_comment():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        text = data.get('text', '')
        images = data.get('images', [])

        # 检查图片大小和数量
        total_size = sum(len(image) for image in images)
        if total_size > 16 * 1024 * 1024:  # 16MB in bytes
            return jsonify({"error": "Total image size exceeds 16MB limit"}), 413
        if len(images) > 4:
            return jsonify({"error": "Maximum 4 images allowed"}), 400

        author = data.get('author', 'Anonymous User')
        date = datetime.now().isoformat()

        with get_db() as conn:
            cursor = conn.execute('INSERT INTO comments (text, images, author, date) VALUES (?, ?, ?, ?)',
                                  (text, json.dumps(images), author, date))
            conn.commit()
            comment_id = cursor.lastrowid

        return jsonify({"id": comment_id, "text": text, "images": images, "author": author, "date": date})
    except Exception as e:
        logger.error(f"Error adding comment: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=7805, debug=True)

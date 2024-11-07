# Comments_Api

```bash
pip install -r requirements.txt

python app.py

pm2 start "gunicorn -w 4 -b 0.0.0.0:Port app:app" --name comments_api
pm2 status
pm2 startup
按提示运行生成的命令
pm2 save
```

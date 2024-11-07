# Comments_Api

```bash
#安装依赖
pip install -r requirements.txt
#初始化sqlite
python app.py
#启动生产服务
pm2 start "gunicorn -w 4 -b 0.0.0.0:Port app:app" --name comments_api
pm2 status
pm2 startup
#按提示运行生成的命令
pm2 save

#删除database某个id行的数据（id用vscode查看）
python deletedata.py <data_id>
```

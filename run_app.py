from flask import Flask
from app.routes import init_routes

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# 初始化路由
init_routes(app)
if __name__ == '__main__':
    app.run(port=5000, debug=True) 
    # app.run(port=5000) 

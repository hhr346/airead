# app.py
from flask import Flask
from routes import init_routes
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 初始化路由
init_routes(app)
if __name__ == '__main__':
    app.run(port=5000) 

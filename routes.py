# routes.py
from flask import request, render_template, jsonify
from summarizer import summarize_content, fetch_rss_content
import SparkApi
import feedparser

# 以下密钥信息从控制台获取   https://console.xfyun.cn/services/bm35
appid = "c29cd28d"     #填写控制台中获取的 APPID 信息
api_secret = "OWMyNzRjZWU0NTEwZDZiMjMzNmU1YmNi"   #填写控制台中获取的 APISecret 信息
api_key ="f3eddb259d1f711e3c6bbdcb3dddecf0"    #填写控制台中获取的 APIKey 信息

# https://www.xfyun.cn/doc/spark/Web.html#_1-%E6%8E%A5%E5%8F%A3%E8%AF%B4%E6%98%8E
domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址
domain = "general"
Spark_url = "wss://spark-api.xf-yun.com/v1.1/chat"  # Lite环服务地址
domain = '4.0Ultra'        # v4.0版本
Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat"  # v4.0环服务地址

text = []
def getText(role,content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

def init_routes(app):
    # 现有的路由
    @app.route('/')
    def home():
        messages = [{'id': 1, 'title': 'Article 1', 'summary': 'Summary of Article 1'},
                    {'id': 2, 'title': 'Article 2', 'summary': 'Summary of Article 2'}]
        return render_template('index.html', messages=messages)

    # 新的路由来处理AI问答
    @app.route('/ask_ai', methods=['POST'])
    def ask_ai():
        data = request.json
        question = data.get('question')
        message_id = data.get('message_id')
        question = getText("user", question)

        # 在这里调用AI的处理逻辑
        SparkApi.answer = ""
        print("星火:", end="")
        SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
        # 获取AI的回答
        summarized_content = SparkApi.answer
        
        # 返回JSON格式的响应
        return jsonify({'answer': summarized_content})

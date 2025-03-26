import glob
import json
import os
from flask import Flask, render_template, request, jsonify
from .createByDoc import createByDoc
from .summarizer import SparkTools
import feedparser
import hashlib

app = Flask(__name__)

def init_routes(app):
    UPLOAD_FOLDER = 'data'  # 文件存储位置
    RSS_FOLDER = 'data/rss'
    KEYWORD_FILE = './data/keyword.txt'

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['RSS_FOLDER'] = RSS_FOLDER
    app.config['KEYWORD_FILE'] = KEYWORD_FILE

    # 确保上传文件夹存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    @app.route('/')
    # 对主页的页面进行路由
    def index():
        return render_template('index.html')

    @app.route('/add_new')
    # 对添加新订阅源的页面进行路由
    def add_new():
        return render_template('add_new.html')

    @app.route('/paper_tool')
    # 对论文工具的页面进行路由
    def paper_tool():
        return render_template('paper_tool.html')

    @app.route('/profile')
    # 对个人资料的页面进行路由
    def profile():
        keyword = load_keyword()
        return render_template('profile.html', keyword=keyword)


    @app.route('/import_rss', methods=['POST'])
    # 处理RSS导入的路由
    def import_rss():
        rss_url = request.form.get('rss_url')  # 接收用户提交的RSS链接
        if not rss_url:
            return jsonify({"status": "error", "message": "RSS链接不能为空"})

        try:
            feed = feedparser.parse(rss_url)
        except Exception as error:
            print(error)
            # if feed.bozo:
            return jsonify({"status": "error", "message": "RSS解析失败"})

        # 解析成功，开始存储内容
        rss_title = feed.feed.title
        rss_hash = hashlib.md5(rss_title.encode('utf-8')).hexdigest()

        # 对每条消息进行遍历，这个键值比较麻烦
        messages = []
        for entry in feed.entries:
            message = {
                "title": entry.title,
                "link": entry.link,
            }
            summary = entry.get('summary') or entry.get('description')
            message['summary'] = summary if summary else "No summary available"

            details = entry.get('content') or entry.get('description')
            # If 'content' is a list or dict with a 'value' key, extract it.
            if isinstance(details, list):
                message['details'] = details[0].get('value') if 'value' in details[0] else details[0]
            elif isinstance(details, dict) and 'value' in details:
                message['details'] = details.get('value')
            else:
                message['details'] = details if details else "No details available"

            date = entry.get('date') or entry.get('pubDate') or entry.get('published')
            message['date'] = date if date else "No date available"

            messages.append(message)
        
        # 存储RSS的订阅源的标题
        with open('data/rss_sources.txt', 'a', encoding='utf-8') as f:
            f.write(f"{rss_hash}--:--{rss_title}--:--{rss_url}\n")

        # 将消息存储到文件中，你需要考虑一下在更新的时候处理重复的消息？
        folder_path = f'data/rss/{rss_hash}'
        os.makedirs(folder_path, exist_ok=True)
        for message in messages:
            message_id = hashlib.md5(message['title'].encode('utf-8')).hexdigest()
            file_name = f"{folder_path}/{message_id}.json"
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(message, f, ensure_ascii=False, indent=4)
        return jsonify({"status": "success", "message": "RSS导入成功"})


    @app.route('/get_sidebar_data')
    # 获取侧边栏订阅的名称
    def get_sidebar_data():
        sidebar_data = []
        
        # 从存储的文本文件中读取RSS订阅源标题
        with open('data/rss_sources.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                parts = line.split('--:--')
                rss_hash, rss_title, rss_url = parts
                sidebar_data.append({
                    "title": rss_title,
                    "id": rss_hash,
                    "url": rss_url
                })
        return jsonify(sidebar_data)

    @app.route('/subscription/<rss_id>')
    # 根据 rss_id 提取并显示相应的RSS内容
    def view_subscription(rss_id):
        messages = []
        folder_path = f'data/rss/{rss_id}'

        # 检查文件夹是否存在
        if os.path.exists(folder_path):
            # 遍历文件夹中的所有JSON文件
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.json'):
                    file_path = os.path.join(folder_path, file_name)
                    
                    # 读取每个JSON文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        message = json.load(f)
                        messages.append(message)  # 将消息添加到列表中

        print(f'Loaded {len(messages)} messages from {folder_path}.')

        # 渲染模板并传递消息列表
        return render_template('subscription.html', rss_id=rss_id, messages=messages)

    @app.route('/messages')
    # 对所有消息的页面进行路由
    def messages():
        messages = []
        # 读取对应的RSS订阅源消息
        files = glob.glob(f'data/rss/*/*.json')
        for file in files:
            # 读取每个JSON文件
            with open(file, 'r', encoding='utf-8') as f:
                message = json.load(f)
                messages.append(message)  # 将消息添加到列表中

        # 渲染模板并传递消息列表
        return render_template('messages.html', messages=messages)


    # 读取关键词文件内容
    def load_keyword():
        try:
            with open(KEYWORD_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    # 将关键词写入文件
    def save_keyword(new_keyword):
        with open(KEYWORD_FILE, 'w', encoding='utf-8') as f:
            f.write(new_keyword)

    @app.route('/save_keyword', methods=['POST'])
    # 保存关键词的路由
    def save_keyword_route():
        # 获取前端发送的新关键词
        new_keyword = request.json.get('keyword', '')
        save_keyword(new_keyword)  # 将新关键词保存到文件
        return jsonify({"message": "关键词已保存"})


    @app.route('/upload_file', methods=['POST'])
    # 论文工具中的上传文件功能
    def upload_file():
        if 'file' not in request.files:
            return 'No file part', 400

        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400

        # 保存文件到指定文件夹
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'process_file.pdf'))
        return 'File successfully uploaded', 200

    @app.route('/generate_ppt', methods=['POST'])
    # 论文工具中的生成PPT
    def generate_ppt():
        try:
            # Set your APPId and APISecret (you can use environment variables)
            APPId = os.getenv('XUNFEI_APPID')
            APISecret = os.getenv('XUNFEI_APISECRET')

            # Initialize the PPT generation process
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'process_file.pdf')
            ppt_generator = createByDoc(APPId, APISecret, filepath)
            
            # Generate the PPT and get the download link
            ppt_url = ppt_generator.get_result()

            # Return the PPT download link to the frontend
            return jsonify({'success': True, 'ppt_url': ppt_url})
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/generate-summary', methods=['POST'])
    # 论文工具中的总结生成
    def generate_summary_route():
        try:
            # Assume 'uploaded_file_path' is the path where the uploaded PDF is saved
            paper_tools = SparkTools()
            uploaded_file_path = os.path.join('data', 'process_file.pdf')
            summary = paper_tools.generate_summary(uploaded_file_path)  # Call the summarizer function
            return jsonify({'summary': summary})
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500

    @app.route('/generate-recommend', methods=['POST'])
    # 资讯列表中的推荐总结生成，思考一下怎么改呢？
    def generate_recommend_route():
        data = request.json
        rss_id = data.get('rss_id')  # 获取POST请求体中的rss_id
        try:
            recommend_tools = SparkTools()
            # 这里先做一个示例，实际上需要查找一下是哪个订阅源
            uploaded_file_path = os.path.join('data', 'rss', rss_id)
            recommend = recommend_tools.generate_recommend(uploaded_file_path)  # Call the summarizer function
            return jsonify({'recommend': recommend})
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500

    @app.route('/ask-question', methods=['POST'])
    # 生成总结后用户可提问
    def ask_question_route():
        data = request.get_json()
        question = data['question']
        
        try:
            paper_tools = SparkTools()
            # Call the ask_question function from summarizer.py
            answer = paper_tools.ask_question(question)
            return jsonify({'answer': answer})
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500

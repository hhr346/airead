import glob
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
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['RSS_FOLDER'] = RSS_FOLDER

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
        return render_template('profile.html')


    @app.route('/import_rss', methods=['POST'])
    # 处理RSS导入的路由
    def import_rss():
        rss_url = request.form.get('rss_url')  # 接收用户提交的RSS链接
        if not rss_url:
            return jsonify({"status": "error", "message": "RSS链接不能为空"})

        feed = feedparser.parse(rss_url)
        if feed.bozo:
            return jsonify({"status": "error", "message": "RSS解析失败"})

        # 解析成功，开始存储内容
        rss_title = feed.feed.title
        rss_hash = hashlib.md5(rss_title.encode('utf-8')).hexdigest()

        messages = []
        for entry in feed.entries:
            message = {
                "title": entry.title,
                "summary": entry.summary if 'summary' in entry else "No summary available",
                "details": entry['content'][0].get('value', 'No details'),
                "link": entry.link,
                "published": entry.published if 'published' in entry else "No date available"
            }
            messages.append(message)
        
        # 存储RSS的订阅源的标题
        with open('data/rss_sources.txt', 'a', encoding='utf-8') as f:
            f.write(f"{rss_hash}--:--{rss_title}--:--{rss_url}\n")

        # 将消息存储到文本文件中
        with open(f'data/rss/{rss_hash}.txt', 'a', encoding='utf-8') as f:
            for message in messages:
                # f.write(f"{message['published']}--:--{message['title']}--:--{message['summary']}--:--{message['link']}\n")
                f.write(f"{message['published']}--:--{message['title']}--:--{message['details']}--:--{message['link']}\n")

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

        # 读取对应的RSS订阅源消息
        try:
            with open(f'data/rss/{rss_id}.txt', 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    parts = line.split('--:--')  # 假设你的数据格式固定
                    if len(parts) == 4:
                        date, title, description, link = parts
                        messages.append({
                            'date': date,
                            'title': title,
                            'description': description,
                            'link': link.strip()  # 去掉末尾换行符
                        })
        except FileNotFoundError:
            messages.append({
                'date': '',
                'title': '订阅源不存在',
                'description': '没有找到相应的RSS订阅源数据',
                'link': '#'
            })

        # 渲染模板并传递消息列表
        return render_template('subscription.html', rss_id=rss_id, messages=messages)

    @app.route('/messages')
    # 对所有消息的页面进行路由
    def messages():
        messages = []
        # 读取对应的RSS订阅源消息
        files = glob.glob(f'data/rss/*.txt')
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        parts = line.split('--:--')  # 假设你的数据格式固定
                        if len(parts) == 4:
                            date, title, description, link = parts
                            messages.append({
                                'date': date,
                                'title': title,
                                'description': description,
                                'link': link.strip()  # 去掉末尾换行符
                            })
            except FileNotFoundError:
                messages.append({
                    'date': '',
                    'title': '订阅源不存在',
                    'description': '没有找到相应的RSS订阅源数据',
                    'link': '#'
                })

        # 渲染模板并传递消息列表
        return render_template('messages.html', messages=messages)

    @app.route('/upload_file', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return 'No file part', 400

        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400

        # 保存文件到指定文件夹
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'process_file.' + file.filename.split('.')[1]))
        return 'File successfully uploaded', 200

    @app.route('/generate_ppt', methods=['POST'])
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

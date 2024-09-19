from flask import Flask, render_template, request, jsonify
import feedparser
import hashlib

app = Flask(__name__)

# 模拟的用户订阅源数据
subscription_sources = [
    {"id": 1, "name": "订阅源1"},
    {"id": 2, "name": "订阅源2"},
    # 可以通过后端代码动态添加或更新这个列表
]

def init_routes(app):
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

    @app.route('/messages')
    # 对所有消息的页面进行路由
    def messages():
        return render_template('messages.html')

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
                "link": entry.link,
                "published": entry.published if 'published' in entry else "No date available"
            }
            messages.append(message)
        
        # 存储RSS的订阅源的标题
        with open('data/rss_sources.txt', 'a', encoding='utf-8') as f:
            f.write(f"{rss_hash}--:--{rss_title}\n")

        # 将消息存储到文本文件中
        with open(f'data/{rss_hash}.txt', 'a', encoding='utf-8') as f:
            for message in messages:
                f.write(f"{message['published']}--:--{message['title']}--:--{message['summary']}--:--{message['link']}\n")

        return jsonify({"status": "success", "message": "RSS导入成功"})


    @app.route('/get_sidebar_data')
    # 获取侧边栏订阅的名称
    def get_sidebar_data():
        sidebar_data = []
        
        # 从存储的文本文件中读取RSS订阅源标题
        with open('data/rss_sources.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                parts = line.split('--:--')
                rss_hash, rss_title = parts
                sidebar_data.append({
                    "title": rss_title,
                    "id": rss_hash
                })
        return jsonify(sidebar_data)

    @app.route('/subscription/<rss_id>')
    # 根据 rss_id 提取并显示相应的RSS内容
    def view_subscription(rss_id):
        messages = []

        # 读取对应的RSS订阅源消息
        try:
            with open(f'data/{rss_id}.txt', 'r', encoding='utf-8') as f:
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

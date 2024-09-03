# routes.py
from flask import request, render_template, jsonify
from summarizer import summarize_content, fetch_rss_content

def init_routes(app):
    """
    @app.route('/')
    def index():
        # 显示欢迎信息，然后通过HTML meta标签在2秒后重定向到订阅页面
        return '''
            <html>
                <head>
                    <meta http-equiv="refresh" content="2;url=/subscribe" />
                </head>
                <body>
                    <h1>欢迎来到RSS订阅网站！</h1>
                    <p>2秒后将自动跳转到订阅页面...</p>
                </body>
            </html>
        '''
    # def index():
    #     return "欢迎来到RSS订阅网站！"

    @app.route('/subscribe', methods=['GET', 'POST'])
    def subscribe():
        if request.method == 'POST':
            rss_url = request.form['rss_url']
            rss_content = fetch_rss_content(rss_url)
            print(rss_content)

            # summary = summarize_content(rss_content)
            # return f"订阅成功！摘要内容: {summary}"

            # 构造HTML来显示RSS内容
            response_html = "<h2>订阅成功！</h2><ul>"
            for title, link, content in rss_content:
                response_html += f"<li><a href='{link}' target='_blank'>{title}</a><p>{content}</p></li>"
            response_html += "</ul>"
            return response_html

        return render_template('subscribe.html')
    """

    @app.route('/')
    def home():
        return render_template('index.html', sources=[])

    @app.route('/subscribe', methods=['POST'])
    def subscribe():
        rss_url = request.form['rss_url']
        # 假设这里成功订阅了 RSS 源，并获取了消息数据
        # 将获取到的源和消息数据传递给前端
        messages = [{'title': 'Example Article 1'}, {'title': 'Example Article 2'}]  # 示例数据
        return render_template('index.html', sources=[rss_url], messages=messages, subscribed=True)

    @app.route('/summarize', methods=['POST'])
    def summarize():
        # 调用你的 API 来生成总结
        summarized_content = "这是一个总结内容的示例。"
        return jsonify({'content': summarized_content})


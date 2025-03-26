'''
获取上传的内容，然后使用AI进行总结，最后将总结内容返回给用户，同时用户可以通过对话框进行提问
'''
import os
import json
import glob
import SparkApi

class SparkTools:
    def __init__(self) -> None:
        self.appid = os.environ.get("XUNFEI_APPID")
        self.api_secret = os.environ.get("XUNFEI_APISECRET")
        self.api_key = os.environ.get("XUNFEI_APIKEY")

        self.domain = '4.0Ultra'        # v4.0版本
        self.Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat"  # v4.0环服务地址
        self.text = []

    def getText(self, role,content):
        jsoncon = {}
        jsoncon["role"] = role
        jsoncon["content"] = content
        self.text.append(jsoncon)

    def getlength(self, text):
        length = 0
        for content in text:
            temp = content["content"]
            leng = len(temp)
            length += leng
        return length

    def checklen(self, text):
        while (self.getlength(text) > 8000):
            del text[0]
        return text
    
    def pdfRead(self, filepath):
        import pdfplumber
        print('Reading pdf...')
        with pdfplumber.open(filepath) as pdf:
            self.pdf_content = ''
            # 循环读取每一页的内容
            for page in pdf.pages:
                self.pdf_content += page.extract_text()
        with open("./data/process_file.txt", 'w', encoding='utf-8') as file:
            file.write(self.pdf_content)
        print('Reading Completed, processing...')

    def generate_summary(self, filepath):
        self.pdfRead(filepath)
        sys_txt = self.pdf_content + "请根据上述文章，用精炼的中文对其进行总结和概括，着重介绍其工作过程和创新点。"
        self.getText("user", sys_txt)

        SparkApi.answer =""
        print("星火:",end ="")
        SparkApi.main(self.appid,self.api_key,self.api_secret,self.Spark_url,self.domain, self.text)
        return SparkApi.answer
    
    def jsonRead(self, filepath):
        print('Reading json...')
        self.json_content = []
        # 读取对应的RSS订阅源消息
        files = glob.glob(f'{filepath}/*.json')
        for i in range(8):
            file = files[i]
            # 读取每个JSON文件
            with open(file, 'r', encoding='utf-8') as f:
                message = json.load(f)
                self.json_content.append(message)  # 将消息添加到列表中

    def getKeyword(self):
        with open("./data/keyword.txt", 'r', encoding='utf-8') as file:
            self.keyword = file.read()

    def generate_recommend(self, filepath):
        self.getKeyword()
        self.jsonRead(filepath)
        sys_txt = str(self.json_content) + f"请根据上面的资讯的json列表里的内容，为用户提供一个相关性和{self.keyword}从高到低的排序的资讯的title和link属性的排序（两个属性都来源于资讯的json文件），注意要包含所有的资讯，对每个资讯都要有一两句话的中文总结。注意回答格式为'为您生成与您{self.keyword}兴趣相关的RSS资讯的排序列表：1.title1(link1) 2.title2(link2)...'"
        self.getText("user", sys_txt)

        SparkApi.answer =""
        print("星火:",end ="")
        SparkApi.main(self.appid,self.api_key,self.api_secret,self.Spark_url,self.domain, self.text)
        return SparkApi.answer
 
    def ask_question(self, question):
        # 受限于上下文，为了不过度累计历史对话导致超额，我们每次都清空历史记录
        # 只输入文章内容和用户的问题
        self.text = []
        with open("./data/process_file.txt", 'r', encoding='utf-8') as file:
            pdf_content = file.read()
        print(pdf_content)
        sys_txt = pdf_content + "\n请根据文章内容回答用户的问题。"
        self.getText("user", sys_txt)
        self.getText("user", question)

        SparkApi.answer =""
        print("星火:",end ="")
        SparkApi.main(self.appid,self.api_key,self.api_secret,self.Spark_url,self.domain, self.text)
        return SparkApi.answer

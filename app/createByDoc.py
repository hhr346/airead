import hashlib
import hmac
import base64
import json
import os
import time
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


class createByDoc():

    def __init__(self, APPId, APISecret, filepath):
        self.APPid = APPId
        self.APISecret = APISecret
        self.header = {}
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.output = self.md5(self.filename)

    # 获取签名
    def get_signature(self, ts):
        try:
            # 对app_id和时间戳进行MD5加密
            auth = self.md5(self.APPid + str(ts))
            # 使用HMAC-SHA1算法对加密后的字符串进行加密
            return self.hmac_sha1_encrypt(auth, self.APISecret)
        except Exception as e:
            print(e)
            return None

    def hmac_sha1_encrypt(self, encrypt_text, encrypt_key):
        # 使用HMAC-SHA1算法对文本进行加密，并将结果转换为Base64编码
        return base64.b64encode(
            hmac.new(encrypt_key.encode('utf-8'), encrypt_text.encode('utf-8'), hashlib.sha1).digest()).decode('utf-8')

    def md5(self, text):
        # 对文本进行MD5加密，并返回加密后的十六进制字符串
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    # 创建任务生成任务
    def create_task(self):

        timestamp = int(time.time())
        signature = self.get_signature(timestamp)

        headers = {
            "appId": self.APPid,
            "timestamp": str(timestamp),
            "signature": signature,
            "Content-Type": "multipart/form-data; charset=utf-8"
        }

        # 提交网络文件
        # body = {
        #     "file_url": "https://openres.xfyun.cn/xfyundoc/2024-05-09/7f69a59d-ca21-4569-a295-14c02e3b0cf5/1715247028782/%E4%BD%9C%E6%96%87.txt",
        #     "file_name": "作文.txt",
        # }
        # data = MultipartEncoder(
        #     fields=body,
        #     boundary='------------------' + str(random.randint(1e28, 1e29 - 1))
        # )

        # 提交本地文件
        # params = {
        #     "file_url": "",
        #     "file_name": "作文.txt",  # 文件名, 带文件名后缀
        #     "file": (
        #         '作文.txt.docx', open('作文.txt', 'rb'),
        #         'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        # }

        params = {
            "file_name": self.filename, 
            "query": "这是一篇学术文献，请用这篇文献生成一个文献汇报的PPT，要求使用浅色背景，逻辑清晰，有图片说明，重点突出，包含细节。", 
            "file": (
                self.output + '.pdf', open(self.filepath, 'rb'),
                'application/pdf'
            ),
            "is_figure": "true",
        }
        data = MultipartEncoder(fields=params)


        headers['Content-Type'] = data.content_type
        url = 'https://zwapi.xfyun.cn/api/aippt/createByDoc'
        self.header = headers
        response =requests.post(url=url, data=data, headers=headers).text
        resp = json.loads(response)
        print(resp)
        if 0 == resp['code']:
            print('创建自定义PPT任务成功')
            return resp['data']['sid']
        else:
            print('创建自定义PPT任务失败')
            return None

    # 轮询任务进度，返回完整响应信息
    def get_process(self, sid):
        print("sid:" + sid)
        print(self.header)
        if (None != sid):
            response = requests.request("GET", url=f"https://zwapi.xfyun.cn/api/aippt/progress?sid={sid}",
                                        headers=self.header).text
            print(response)
            return response
        else:
            return None

    # 获取PPT，以下载连接形式返回
    def get_result(self):
        # 创建PPT生成任务
        task_id = self.create_task()
        # PPTurl = ''
        # 轮询任务进度
        while (True):
            time.sleep(1)
            response = self.get_process(task_id)
            resp = json.loads(response)
            process = resp['data']['process']
            if (process == 100):
                PPTurl = resp['data']['pptUrl']
                break
        return PPTurl

if __name__ == "__main__":
    try:
        # Set your APPId and APISecret (you can use environment variables)
        APPId = os.getenv('XUNFEI_APPID')
        APISecret = os.getenv('XUNFEI_APISECRET')

        # Initialize the PPT generation process
        filepath = os.path.join('../data', 'process_file.pdf')
        ppt_generator = createByDoc(APPId, APISecret, filepath)
        
        # Generate the PPT and get the download link
        ppt_url = ppt_generator.get_result()
    except Exception as e:
        print(e)

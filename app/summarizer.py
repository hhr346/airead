'''
获取RSS的内容，然后使用AI进行总结，最后将总结内容返回给用户，同时用户可以通过对话框进行提问
'''
import SparkApi
import feedparser

def getText(role,content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

def checklen(text):
    while (getlength(text) > 8000):
        del text[0]
    return text
    
def fetch_rss_content(rss_url):
    '''
    RSS eg: https://www.teach.ustc.edu.cn/category/notice/feed
    将RSS的内容提取出来，返回界面
    '''
    feed = feedparser.parse(rss_url)

    # for entry in feed.entries:
    #     if 'content' in entry and entry['content']:
    #         detailed_content = entry['content'][0].get('value', '无内容')
    #     else:
    #         detailed_content = entry.get('summary', '无摘要')

    # content = [entry.title + " " + entry.link for entry in feed.entries]
    # content = [entry.title + " " + entry.link + "\n" + entry['content'][0].get('value', '无内容') for entry in feed.entries]
    # return "\n\n".join(content)

    content = []
    for entry in feed.entries:
        title = entry.get('title', '无标题')
        link = entry.get('link', '#')
        detailed_content = entry['content'][0].get('value', '无内容')
        content.append((title, link, detailed_content))
    return content

def summarize_content(rss_content):
    # 使用已有API进行内容总结的逻辑
    print('Reading...')
    fn = open("./record.txt", 'r', encoding='utf-8')

    # 读取方式需要改进，受限于上下文长度，将文档拆分为多个部分，按照---分成多条消息，依次进行输入
    # 可能需要对每个文章分开总结了，长的文档压根就不行，这样轮流进行总结到文档中，然后再重新读取文档进行分类，这样算是比较好的方式？

    # 然后接近了超过上下文长度的时候就进行下一个文档
    # 使用q进行当前文档的退出，进入下一个文档询问

    pre_txt = fn.read()
    fn.close()
    getText("user", pre_txt)
    input(text)

    sys_txt = "上面的文档里有很多文章，每一篇文章用-----隔开。每一篇内部的格式为NO.:, Title:, Contents:, 请你总结每篇文章的中心含义，为我生成一份综合的简报，要求内容简练且有科学性。特别注意要进行不同主题的分类，一个主题下对应多个文章总结条目。每一条总结条目要在括号内说明对应的文章的NO.。开头为：好的，为您生成的简报如下："

    system_prompt = getText("user", sys_txt)
    input(text)

    SparkApi.answer = ""
    print("星火:",end ="")
    SparkApi.main(appid,api_key,api_secret,Spark_url,domain,system_prompt)
    getText("assistant",SparkApi.answer)

    f = open('./summary.txt', 'w', encoding='utf-8')
    f.write(SparkApi.answer)
    f.close()
    summarized_content = SparkApi.answer

    while(1):
        getText("system", "现在根据你学习到的内容，回答用户的问题。")
        Input = input("\n" +"我:")
        # question = checklen(getText("user",Input))
        question = getText("user",Input)
        SparkApi.answer =""
        print("星火:",end ="")
        SparkApi.main(appid,api_key,api_secret,Spark_url,domain,question)
        getText("assistant",SparkApi.answer)

    return summarized_content


def pdfRead():
    import PyPDF2
    '''
    Process the PDF file to create a summary to chat with AI
    Use the api to create a ppt
    '''
    # 打开PDF文件
    with open('your_paper.pdf', 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        # 循环读取每一页的内容
        for page in reader.pages:
            text += page.extract_text()
    print(text)

    return text

def pdf2ppt():
    '''
    Use the api to create a ppt
    https://www.xfyun.cn/doc/spark/PPTGeneration.html#%E6%8E%A5%E5%8F%A3%E4%B8%8E%E9%89%B4%E6%9D%83
    可以直接上传pdf和要求，或者可以转为文本后上传，可以测试一下二者的效果的区别
    时间生成上和生成质量上
    '''

if __name__ == "__main__":
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


    #初始上下文内容，当前可传system、user、assistant 等角色
    text =[
        # {"role": "system", "content": "你现在扮演李白，你豪情万丈，狂放不羁；接下来请用李白的口吻和用户对话。"} , # 设置对话背景或者模型角色
        # {"role": "user", "content": "你是谁"},  # 用户的历史问题
        # {"role": "assistant", "content": "....."} , # AI的历史回答结果
        # # ....... 省略的历史对话
        # {"role": "user", "content": "你会做什么"}  # 最新的一条问题，如无需上下文，可只传最新一条问题
    ]

# AIread

> 一个RSS+大模型的网站设计
>

面对大量的信息投喂，如何找到贴合自己研究关注领域的内容？针对你的研究领域来进行一个搜索，所以理解能力很重要。找到相关的内容优先推荐，太多了看不过来。手动订阅关键词，并且知道是真的相关！

相比于RSS，亮点工作有以下：

一方面是对搜集的信息进行总结整理，并且可以进行提问。

另一方面是直接对原文内容进行读取，这样才可以有更多的细节可以去提取。这对token和上下文的要求就很高了。



## 功能设计

### RSS订阅构建

用户自行导入的RSS链接进行订阅

可以提供一些常用的网站订阅推荐，或者直接进行搜索的功能



### RSS总结

调用大模型对订阅内容进行总结，最好能爬取内部的文章的具体内容，然后整体进行识别读取，或者只对摘要进行一个进一步处理

然后再对分条目的总结进行一个日报的生成，最好能在服务器端进行处理。



### RSS重点推荐

通过用户自行定义的研究领域和兴趣点，来推荐相关的条目和细节。



### 论文阅读写作

对完整论文进行读取和总结，提供一个调研的展示功能，展示文字内容或者ppt模板。

并提供写作辅导，根据用户设定的主题建立文章大纲，并在用户进一步进行段落的细化和细节完善之后对段落进行下一步的续写。



## 前端页面设计构建

前端页面设计可以先做一个UI设计，然后后续用一些模板去具体实现

按照上述的一个过程分页面来进行设计。



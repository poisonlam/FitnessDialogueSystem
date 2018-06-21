import urllib.request
import pickle
import re
from pymongo import MongoClient
import pymongo

class Tool:
    RemoveImg = re.compile('<img.*?>| {7}|')
    # 匹配图片标签
    RemoveAddr = re.compile('<a.*?>|</a>')  # 匹配链接标签
    ReplaceLine = re.compile('<tr>|<div>|</div></p>')  # 匹配换行符的标签
    ReplaceTD = re.compile('<td>')  # 匹配制表符
    ReplacePara = re.compile('<p.*?>')  # 匹配段落开头
    ReplaceBR = re.compile('<br><br>|<br>')  # 匹配换行和双换行
    RemoveTag = re.compile('<.*?>')  # 匹配其余的标签

    def replace(self, x):
        x = re.sub(self.RemoveImg, "", x)  # 删除图片
        x = re.sub(self.RemoveAddr, "", x)  # 删除链接
        x = re.sub(self.ReplaceLine, "\n", x)  # 替换换行符
        x = re.sub(self.ReplaceTD, "", x)  # 将制表符替换
        x = re.sub(self.ReplacePara, "\n  ", x)  # 段落开头替换
        x = re.sub(self.ReplaceBR, "\n", x)
        x = re.sub(self.RemoveTag, "", x)  # 删除其余标签
        return x.strip()

class Action_lib:
    def __init__(self, url):
        self.url = url
        self.tool = Tool()
        self.file = None

    # 获取网页代码
    def gethtml(self):
        url = self.url
        request = urllib.request.Request(url)
        respones = urllib.request.urlopen(request)
        html = respones.read()
        html = html.decode('utf-8')
        file = open("html.txt", "w+")
        file.write(html)
        return html

    def get_name(self, html):
        #获取动作名称
        pattern_actionname = re.compile('<h1 class="video-title">(.*?)</h1>',re.S)
        actionname = re.findall(pattern_actionname, html)
        return actionname

    def get_type(self, html):
        # 获取动作类型
        pattern_actiontype = re.compile('<p class="p-mg-bottom">类型&nbsp;:&nbsp;<em>(.*?)</em></p>', re.S)
        actiontype = re.findall(pattern_actiontype, html)
        return actiontype

    def get_level(self, html):
        # 获取动作级别
        pattern = re.compile('<p>级别&nbsp;:&nbsp;<.*?><em>(.*?)</em></a></p>',re.S)
        level = re.findall(pattern, html)
        # print(level)
        return level

    def get_tips(self, html):
        # 获取动作要领
        pattern_tips = re.compile('<div class="guide-text">.*?<pre class="cont".*?>(.*?)</pre>', re.S)
        actiontips = re.findall(pattern_tips, html)
        contents = []
        for item in actiontips:
            content = self.tool.replace(item)
            contents.append(content)
            #print(item)
        return contents

    def get_maingoal(self, html):
        # 获取受训肌肉及肌肉群
        pattern_goal_main = re.compile('<p class="p-mg-bottom">主要肌肉群&nbsp;:&nbsp;<.*?><em>(.*?)</em>', re.S)
        main_goal = re.findall(pattern_goal_main, html)
        return main_goal

    def get_othergoal(self, html):
        # pattern_goal_other = re.compile('<p class="p-mg-bottom">主要肌肉群&nbsp;:&nbsp;<.*?><em>.*?</em>.*?<a.*?>(.*?)</a>', re.S)
        pattern_goal_other = re.compile('<!-- <p>其他肌肉&nbsp;:&nbsp;<em></em></p> -->.*?<p>其他肌肉&nbsp;:&nbsp;<em>(.*?)</em>', re.S)
        other_goal = re.findall(pattern_goal_other, html)
        contents = []
        for item in other_goal:
            content = self.tool.replace(item).replace('\t', '').replace('\n', '')
            contents.append(content)
        #print(contents)
        return contents

    def get_require(self, html):
        # 获取动作器械要求
        pattern_require = re.compile('<div class="info-main-section">.*?<a href="/dongzuo/\?equipment.*?>(.*?)</a>', re.S)
        actionrequire = re.findall(pattern_require, html)
        return actionrequire

    def get_description(self, html):
        #获取动作描述
        pattern_describe = re.compile('<meta name="description" content="(.*?)">',re.S)
        description = re.findall(pattern_describe, html)
        return description

    def start(self, file):
        #开始爬取数据
        html = self.gethtml()
        #print("已获得源代码，正在处理......")
        action_name = self.get_name(html)
        type = self.get_type(html)
        level  = self.get_level(html)
        tips = self.get_tips(html)
        main_goal = self.get_maingoal(html)
        other_goal = self.get_othergoal(html)
        require = self.get_require(html)
        description = self.get_description(html)
        #print("动作数据集创建成功，文件名为： Action_lib.txt")
        # file.write(self.tool.replace(str(description)))
        # file.write('\n')
        # file.write(self.tool.replace(str(tips)))
        # file.write('\n\n')
        return action_name,type,level,tips,main_goal,other_goal,require,description

url = 'https://www.hiyd.com/dongzuo/1'
source = 'https://www.hiyd.com/dongzuo/'

def filename(title):
    if title:
        file = open(title + ".txt", "w+")
    else:
        print("文件创建出错！")
    return file

action_lib = filename('Action_lib')


client = MongoClient('localhost', 27017)
ActionDB = client.ActionDB
ActionTable = ActionDB.action
for i in range(1602):
    new_add = source + str(i+1)
    #print(new_add)
    data = Action_lib(new_add)
    actions = {}
    action_name, Atype, level, tips, main_goal, other_goal, require, description = data.start(action_lib)
    actions['name'] = str(action_name).replace('[','').replace(']','').replace('\'','')
    actions['type'] = str(Atype).replace('[','').replace(']','').replace('\'','')
    actions['level'] = str(level).replace('[','').replace(']','').replace('\'','')
    actions['mainMuscle'] = str(main_goal).replace('[','').replace(']','').replace('\'','')
    actions['assistantMuscle'] = str(other_goal).replace('[','').replace(']','').replace('\'','')
    actions['equipment'] = str(require).replace('[','').replace(']','').replace('\'','')
    actions['details'] = str(tips).replace('\r\n','').replace('[','').replace(']','').replace('\'','').replace('\r','')
    actions['describe'] = str(description).replace('\n','').replace('[','').replace(']','').replace('\'','').replace('\r','')
    #将一个动作信息存入数据集中
    ActionTable.insert_one(actions)




import json
import time
from dateutil import parser
import spacy
import requests
import re
import os
from clang.cindex import Index, CursorKind, TokenKind

# with open("commits.json","r") as f:
#     commits=json.load(f)

def countAFD(commits,id):
    time=""
    file_list={}
    for commit in commits : 
        if commit["commit"] == id:
            time=commit["date"]
            for file_name in commit["files"].keys():
                file_list[file_name]=0
    
    for commit in commits : 
        if judgeTime(time,commit["date"]):
            for file_name in commit["files"].keys():
                if file_name in file_list.keys():
                    file_list[file_name]=file_list[file_name]+1

    if len(file_list)==0:
        return 1

    afd=0
    # print("size",len(file_list))
    for file_name in file_list.keys():
        afd =  afd+file_list[file_name]
    
    afd=afd/len(file_list)

    return afd

def countTFD(commits,id):
    time=""
    file_list={}
    for commit in commits : 
        if commit["commit"] == id:
            time=commit["date"]
            now = parser.parse(time)
    
    for commit in commits : 
        time2=commit["date"]
        tmp_time = parser.parse(time2)
        if tmp_time<now:
            for file_name in commit["files"].keys():
                if file_name not in file_list.keys():
                    file_list[file_name]=["","",""]
                    file_list[file_name][0]=tmp_time
                    file_list[file_name][1]=tmp_time
                if tmp_time> file_list[file_name][0]:
                    file_list[file_name][0]=tmp_time
                elif tmp_time> file_list[file_name][1]:
                    file_list[file_name][1]=tmp_time
                d=file_list[file_name][0]-file_list[file_name][1]
                file_list[file_name][2]=d.days
            
    tfd=0
    for file_name in file_list.keys():
        tfd=tfd+file_list[file_name][2]
    return tfd/len(file_list)

def countEMC_EMI(commits,id):
    time=""
    file_list={}
    for commit in commits : 
        if commit["commit"] == id:
            time=commit["date"]
            now = parser.parse(time)
    
    for commit in commits : 
        time2=commit["date"]
        tmp_time = parser.parse(time2)
        if tmp_time<now:
            for file_name in commit["files"].keys():
                if file_name not in file_list.keys():
                    file_list[file_name]=["","","",0]
                    file_list[file_name][0]=tmp_time
                    file_list[file_name][1]=tmp_time
                if tmp_time> file_list[file_name][0]:
                    file_list[file_name][0]=tmp_time
                elif tmp_time< file_list[file_name][1]:
                    file_list[file_name][1]=tmp_time
                d=file_list[file_name][0]-file_list[file_name][1]
                file_list[file_name][2]=d.days
                file_list[file_name][3]=file_list[file_name][3]+1
            
    emc=0
    emi=0
    for file_name in file_list.keys():
        emc=emc+file_list[file_name][2]
        emi=emi+file_list[file_name][2]/file_list[file_name][3]
    return emc/len(file_list),emi/len(file_list)

def countSRM(commits,id):
    time=""
    file_list=[]
    for commit in commits : 
        if commit["commit"] == id:
            time=commit["date"]
            now = parser.parse(time)
            file_list.append(commit["files"].keys())
    srm=len(file_list)
    for commit in commits : 
        time2=commit["date"]
        tmp_time = parser.parse(time2)
        if tmp_time>now:
            for file_name in commit["files"].keys():
                if file_name in file_list:
                    srm=srm-1
    return srm

def countLME(commits,id):
    time=""
    lme=0
    for commit in commits : 
        if commit["commit"] == id:
            time=commit["date"]
            now = parser.parse(time)
            lem=len(commit["files"])
    return lme

def countPR(commits,id):
    author=""
    for commit in commits : 
        if commit["commit"] == id:
            author=commit["author"]
    sum=0
    recommit=0
    for commit in commits : 
        sum=sum+len(commit["files"])
        if commit["author"] == author:
            recommit= recommit+len(commit["files"])
    
    return 1-recommit/sum

def countIF(commits,id):
    pf=0
    mf=0
    ff=0
    time=""
    author=""
    pf1=0
    pf2=0
    for commit in commits : 
        if commit["commit"] == id:
            time=commit["date"]
            now = parser.parse(time)
            author=commit["author"]
    ff1=ff2=0
    for commit in commits : 
        time2=commit["date"]
        tmp_time = parser.parse(time2)
        if tmp_time<now:
            ff2+=1
            if len(commit["files"])!= 0:
                pf2=pf2+1
                if author==commit["author"]:
                    pf1=pf1+1
                    ff1+=1
    pf=pf1/pf2
    ff=ff1/ff2
    return (pf+ff+mf)/3

def countVLP(commits,id):

    # print(spacy.__version__)  # 检查 spacy 版本
    # print(spacy.util.get_package_path("en_core_web_sm"))  # 检查模型路径
    
    nlp = spacy.load(r"C:\Users\zcg\AppData\Local\Programs\Python\Python39\Lib\site-packages\en_core_web_sm\en_core_web_sm-3.7.0")
    doc=""
    vlp=0
    for commit in commits:
        if commit["commit"] == id :
            doc=commit["info"]
    doc=nlp(doc)
    tokens = [token for token in doc]  # 将分词结果转换为列表

    # 遍历句子中的每个词，检查是否存在名词 + 介词 + 名词的结构
    for i in range(len(tokens) - 2):  # 确保有足够的词可以组成三元组
        # 检查词性是否符合名词 + 介词 + 名词的结构
        if (
            tokens[i].pos_ in ("NOUN", "PROPN")  # 第一个词是名词
            and tokens[i + 1].pos_ == "ADP"  # 第二个词是介词
            and tokens[i + 2].pos_ in ("NOUN", "PROPN")  # 第三个词是名词
        ):
            vlp=1
        
    for token in doc:
        # 检查是否有动词
        if token.pos_ == "VERB":
            # 检查动词是否有宾语
            for child in token.children:
                if child.dep_ in ("dobj", "obj"):  # dobj: 直接宾语, obj: 宾语
                    vlp=1
        if token.pos_ == "ADP":  # ADP 是介词的词性标注
            # 检查介词是否有宾语
            for child in token.children:
                if child.dep_ in ("pobj", "obj"):  # pobj: 介词宾语, obj: 宾语
                    vlp=1
    return vlp

def countCCP(commits,id,vlp):
    if vlp==0:
        return 0
    ccp=0
    doc=""
    for commit in commits:
        if commit["commit"] == id :
            doc=commit["info"]
    words=["add","insert","delete","remove","update","modify","fix","dispath","clone","merge","close","build","init"]
    for word in words:
        if word in doc:
            ccp=1
    return ccp
   
def get_code_block_comments(file_path):
    # 创建索引并解析文件
    index = Index.create()
    translation_unit = index.parse(file_path)

    # 遍历 AST 提取代码块和注释
    code_blocks = []

    def visit_node(node):
        # 检查节点是否为代码块（函数、类、循环等）
        if node.kind in [
            CursorKind.FUNCTION_DECL,  # 函数
            CursorKind.CLASS_DECL,    # 类
            CursorKind.FOR_STMT,       # for 循环
            CursorKind.WHILE_STMT,     # while 循环
            CursorKind.IF_STMT,        # if 语句
        ]:
            # 提取代码块的起始和结束位置
            start_line = node.extent.start.line
            end_line = node.extent.end.line

            # 提取代码块关联的注释
            comments = []
            for token in node.get_tokens():
                if token.kind == TokenKind.COMMENT:
                    comment_line = token.extent.start.line
                    if start_line - 5 <= comment_line <= end_line + 1:  # 注释在代码块附近
                        comments.append(token.spelling)

            # 记录代码块及其注释
            code_blocks.append({
                "kind": node.kind.name,
                "name": node.spelling or "anonymous",  # 匿名代码块（如循环）
                "start_line": start_line,
                "end_line": end_line,
                "comments": comments,
            })

        # 递归遍历子节点
        for child in node.get_children():
            visit_node(child)

    # 从根节点开始遍历
    visit_node(translation_unit.cursor)

    return code_blocks

def judgeTime(time1,time2):
    date1=parser.parse(time1)
    date2=parser.parse(time2)
    return date1>date2

def countSMCC(owner, repo):
    smcc=0
    pattern = r'^\d+\.\d+\.\d+(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$'
    # GitHub API URL for releases
    os.environ['NO_PROXY'] = '*'
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    
    # Send a GET request to the GitHub API
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        releases = response.json()
        
        # Extract and print the names of the releases
        for release in releases:
            # print(f"Release Name: {release['name']}, Tag: {release['tag_name']}")
            if  re.match(pattern, release['tag_name']) is not None:
                smcc=1
    else:
        print(f"Failed to fetch releases. Status code: {response.status_code}")
    return smcc

# id="acc9084044438bb1de89fef83e826fd9d5e096db"
# afd=countAFD(commits,id)
# tfd=countTFD(commits,id)
# emc,emi=countEMC_EMI(commits,id)
# srm=countSRM(commits,id)
# lme=countLME(commits,id)
# smcc=countSMCC("OpenCV","OpenCV")
# vlp=countVLP(commits,id)
# ccp=countCCP(commits,id,vlp)
# print("count done")


# result={}
# result["Secondary Scores"]={}
# result["Tertiary Scores"]={}
# result["Tertiary Scores"]["Accuracy of Failure Diagnosis"]=afd%10
# result["Tertiary Scores"]["Time of Failure Diagnosis"]=tfd
# result["Tertiary Scores"]["Efficiency of Modification Cycles"]=emc%10
# result["Tertiary Scores"]["Efficiency of Modification Implementation"]=emi%10
# result["Secondary Scores"]["Success Rate of Modifications"]=srm
# result["Secondary Scores"]["Localization of Modification Effects"]=lme
# result["Tertiary Scores"]["Software Modification Control Capability"]=smcc
# result["Tertiary Scores"]["Comprehensible Cues Proportion"]=ccp
# result["Tertiary Scores"]["Valid Leads Proportion"]=vlp

# with open("result_OpenCV4X.json","w+") as fp:
#     json.dump(result,fp)
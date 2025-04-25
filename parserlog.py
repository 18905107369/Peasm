import json
from dateutil import parser
file_name="commit.log"
file=open(file_name,"r",encoding="utf-8")
data=[]
a=[]
for line in file.readlines():
    if line.startswith("commit"):
        data.append(a)
        a=[]
        a.append(line)
    else:
        a.append(line)
data.append(a)
data.pop(0)

print(len(data))
commits=[]
for commit in data:
    c={}
    file_changes={}
    tmp=""
    for line in commit:
        if "commit" in line:
            c["commit"]=line.split(" ")[-1].replace("\n","")
        elif "Author" in line:
            c["author"]=line.split(" ")[-1]
        elif "Date: " in line:
            t=line.split("Date:")[-1].strip().split(" ")[0:-1]
            time=' '.join(t)
            c["date"]=time
        elif "|" in line:
            s=line.split("|")
            file_name=s[0].strip()
            if "=>" in file_name:
                file_name=file_name.split("=> ")[-1].replace("}","")
            inse=0
            dele=0
            if "+" in s[1]:
                inse=1
            if "-" in s[1]:
                dele=1
            file_change={}
            file_change["name"]=file_name.strip()
            file_change["ins"]=inse
            file_change["del"]=dele
            file_changes[file_name]=file_change
        # elif "files changed" in line:
        #     ss=line.split(",")
        #     c["files_changed"]=ss[0].split(" ")[0]
        #     c["insertions"]=ss[1].split(" ")[0]
        #     c["deletions"]=ss[2].split(" ")[0]
        elif line.startswith("    ") :
            tmp=tmp+line.strip()

    # tmp.replace("\n",". ")
    # tmp.lstrip()
    # tmp.replace("    "," ")
    c["info"]=tmp
    c["files"]=file_changes
    commits.append(c)

with open("commits.json","w+") as fp:
    json.dump(commits,fp)
        
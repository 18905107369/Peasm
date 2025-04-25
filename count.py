from countMetric import *
from parserCode import *
import json


dir=r"E:\paper3\project\rncp\react-native-code-push"
id_path="id.txt"
with open("commits.json","r") as f:
    commits=json.load(f)



with open(id_path, 'r', encoding='utf-8') as file:
    # 逐行读取文件内容
    lines = file.readlines()
for line in lines:
    id=line.strip()
    print(id)
    afd=countAFD(commits,id)
    tfd=countTFD(commits,id)
    emc,emi=countEMC_EMI(commits,id)
    srm=countSRM(commits,id)
    lme=countLME(commits,id)
    smcc=countSMCC("microsoft","react-native-code-push")
    vlp=countVLP(commits,id)
    ccp=countCCP(commits,id,vlp)
    print("count done")


    result={}
    result["Secondary Scores"]={}
    result["Tertiary Scores"]={}
    result["Tertiary Scores"]["Accuracy of Failure Diagnosis"]=afd%10
    result["Tertiary Scores"]["Time of Failure Diagnosis"]=tfd
    result["Tertiary Scores"]["Efficiency of Modification Cycles"]=emc%10
    result["Tertiary Scores"]["Efficiency of Modification Implementation"]=emi%10
    result["Secondary Scores"]["Success Rate of Modifications"]=srm
    result["Secondary Scores"]["Localization of Modification Effects"]=lme
    result["Tertiary Scores"]["Software Modification Control Capability"]=smcc
    result["Tertiary Scores"]["Comprehensible Cues Proportion"]=ccp
    result["Tertiary Scores"]["Valid Leads Proportion"]=vlp

    files=get_commit_files(commits,id,dir)
    # print(len(files))
    ds,c=countDS_C(files)
    cm=countCM(files)
    mc=countMC(files,dir)
    ac,cs=countAC_CS(files)
    print("done")

    result["Tertiary Scores"]["Adequacy of Comments"]=ac
    result["Tertiary Scores"]["Comment Specification"]=cs
    result["Tertiary Scores"]["Code Specification"]=1
    result["Tertiary Scores"]["Code Modifiability"]=cm
    result["Tertiary Scores"]["Configurability"]=c
    result["Secondary Scores"]["Modular Cohesion"]=mc
    result["Tertiary Scores"]["Data Specification"]=ds
    result["Tertiary Scores"]["Modifications Complexity"]=mc2

    with open(f"result_rncp_{id}.json","w+") as fp:
        json.dump(result,fp)


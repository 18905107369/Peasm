import json
id_path="id.txt"
with open("commits.json","r") as f:
    commits=json.load(f)



with open(id_path, 'r', encoding='utf-8') as file:
    # 逐行读取文件内容
    lines = file.readlines()

for line in lines:
    id=line.rstrip()
    with open(f"result_rncp_{id}.json","r") as f:
        result=json.load(f)
        analyzability=result["Tertiary Scores"]["Accuracy of Failure Diagnosis"]*0.25+result["Tertiary Scores"]["Time of Failure Diagnosis"]*0.25+result["Tertiary Scores"]["Valid Leads Proportion"]*0.25+result["Tertiary Scores"]["Comprehensible Cues Proportion"]*0.25
        moduarity=analyzability=result["Secondary Scores"]["Modular Cohesion"]    
        standardizability=0.5*result["Tertiary Scores"]["Data Specification"] + \
            0.5*(0.33*result["Tertiary Scores"]["Adequacy of Comments"]+0.33*result["Tertiary Scores"]["Comment Specification"]+0.33*result["Tertiary Scores"]["Code Specification"])
        Modifiability=0.33*result["Tertiary Scores"]["Software Modification Control Capability"] + \
            0.33*(0.5*result["Tertiary Scores"]["Code Modifiability"]+0.5*result["Tertiary Scores"]["Configurability"]) + \
            0.33*(0.33*result["Tertiary Scores"]["Efficiency of Modification Cycles"]+0.33*result["Tertiary Scores"]["Efficiency of Modification Implementation"]+0.33*result["Tertiary Scores"]["Modifications Complexity"])
        Stability=0.5*result["Secondary Scores"]["Localization of Modification Effects"]+0.5*result["Secondary Scores"]["Success Rate of Modifications"]
        score=(analyzability+moduarity+standardizability+Modifiability+Stability)/5
        print(id,score)
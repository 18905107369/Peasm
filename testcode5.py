from transformers import RobertaTokenizer, T5EncoderModel
import time

start=time.time()

tokenizer = RobertaTokenizer.from_pretrained('Salesforce/codet5-base')
model = T5EncoderModel.from_pretrained('Salesforce/codet5-base')

import json
data_path = "oodt_info.json"
with open(data_path, "r") as f:
    data_dict = json.loads(f.read())

model.eval()
result_Dict = {}
code_dict = {}
path_dict = {}


for comp, comp_info in data_dict.items():
    for class_name, class_info in comp_info.items():

        body_text = class_info["body"][:512]
        input_ids2 = tokenizer(body_text, return_tensors="pt").input_ids   
        out2 = model(input_ids = input_ids2)
        vector_list2 = out2.last_hidden_state[0,-1,:].tolist()
        code_dict[class_name] = vector_list2


with open("oodt_code_info_bert.json", "w") as f:
    json.dump(code_dict, f)

end=time.time()

print(str(end-start))
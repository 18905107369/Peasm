import re
import xgboost as xgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 1. 读取Excel文件
file_path = 'dataset.xlsx'  # 替换为你的Excel文件路径
df = pd.read_excel(file_path)

# 2. 分离特征和目标变量
# 假设最后一列是目标变量，其余列是特征
X = df.iloc[:, :-1]  # 所有行，除最后一列外的所有列
y = df.iloc[:, -1]   # 所有行，最后一列

# 3. 将数据集分为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. 转换为XGBoost的DMatrix格式
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# 5. 设置XGBoost参数
params = {
    'objective': 'reg:squarederror',  # 回归任务，使用平方误差作为损失函数
    'max_depth': 6,                   # 树的最大深度
    'eta': 0.1,                       # 学习率
    'subsample': 0.8,                 # 每次建树时使用的样本比例
    'colsample_bytree': 0.8,          # 每次建树时使用的特征比例
    'seed': 42,                       # 随机种子
    'eval_metric': 'rmse'             # 评估指标为均方根误差
}

# 6. 训练模型
num_rounds = 100  # 迭代次数
model = xgb.train(params, dtrain, num_rounds)

# 7. 评估模型
y_pred = model.predict(dtest)
y_pred_binary = [1 if p > 0.5 else 0 for p in y_pred]  # 将概率转换为类别
accuracy = accuracy_score(y_test, y_pred_binary)
print(f'模型准确率: {accuracy:.4f}')

def check_cpp_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    anti_get=anti_set=anti_name=0
    # 正则表达式匹配方法定义
    method_pattern = re.compile(r'(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{?')
    # 正则表达式匹配变量定义
    variable_pattern = re.compile(r'(\w+)\s+(\w+)\s*;')

    # 存储方法信息
    methods = []
    for match in method_pattern.finditer(content):
        return_type, method_name, params = match.groups()
        methods.append((return_type, method_name, params))

    # 存储变量信息
    variables = []
    for match in variable_pattern.finditer(content):
        var_type, var_name = match.groups()
        variables.append((var_type, var_name))

    # 检查规则
    for return_type, method_name, params in methods:
        # 1. 检查 Get 方法没有返回值
        if method_name.startswith("Get") and return_type == "void":
            # print(f"错误: Get 方法 '{method_name}' 没有返回值")
            anti_get+=1

        # 2. 检查 Set 方法存在返回值
        if method_name.startswith("Set") and return_type != "void":
            # print(f"错误: Set 方法 '{method_name}' 存在返回值")
            anti_set+=1

        # 3. 检查方法名称与实际返回类型是否一致
        if method_name.startswith("Get"):
            expected_type = method_name[3:]  # 去掉 "Get" 前缀
            if expected_type.lower() != return_type.lower():
                # print(f"错误: 方法 '{method_name}' 预期返回类型为 '{expected_type}'，实际为 '{return_type}'")
                anti_name+=1

    # for var_type, var_name in variables:
    #     # 4. 检查变量名称与实际类型是否一致
    #     if var_name.startswith("int") and var_type != "int":
    #         print(f"错误: 变量 '{var_name}' 预期类型为 'int'，实际为 '{var_type}'")
    #     if var_name.startswith("str") and var_type != "string":
    #         print(f"错误: 变量 '{var_name}' 预期类型为 'string'，实际为 '{var_type}'")

def countAntiPatten(commits,id,files):
    info=""
    files={}
    t1=0
    t2=0
    anti_modify=0
    for commit in commits : 
        if commit["commit"] == id:
            files=commit["files"]
            info=commit["info"]
    if "fix" in info:
        t1=1
    t2=len(files)

    if t1==0 and t2!=0:
        anti_modify=1
    if t1!=0 and t2==0:
        anti_modify=1
    anti_get=anti_set=anti_name=0
    for file in files:
        g,s,n=check_cpp_file(file)
        anti_get+=g
        anti_set+=s
        anti_name+=n
    return anti_get,anti_set,anti_name,anti_modify
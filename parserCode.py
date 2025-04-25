from collections import defaultdict
from clang.cindex import Index, CursorKind, TokenKind
import json
import os
from glob import glob
import chardet
from clang.cindex import Config
import re
Config.set_library_file("D:\\LLVM-18.1.5\\bin\\libclang.dll")

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
            comments = {}
            for token in node.get_tokens():
                if token.kind == TokenKind.COMMENT:
                    comment_line = token.extent.start.line
                    if start_line - 5 <= comment_line <= end_line + 1:  # 注释在代码块附近
                        comments[token.spelling]=comment_line

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

def build_module_dependency_graph(file_path):
    # 创建索引并解析文件
    index = Index.create()
    translation_unit = index.parse(file_path)

    # 存储模块和它们的关联关系
    modules = {}  # 模块名称 -> 模块信息
    dependencies = {}  # 模块名称 -> 依赖的模块列表

    # 遍历 AST 提取模块和关联关系
    def visit_node(node):
        # 提取模块（函数、类、命名空间等）
        if node.kind in [
            CursorKind.FUNCTION_DECL,  # 函数
            CursorKind.CLASS_DECL,    # 类
            CursorKind.NAMESPACE,      # 命名空间
        ]:
            module_name = node.spelling or "anonymous"
            modules[module_name] = {
                "kind": node.kind.name,
                "location": f"{node.location.file}:{node.location.line}",
            }

            # 初始化依赖关系
            if module_name not in dependencies:
                dependencies[module_name] = []

        # 提取模块之间的调用关系
        if node.kind == CursorKind.CALL_EXPR:  # 函数调用
            caller = node.semantic_parent.spelling or "anonymous"
            callee = node.referenced.spelling or "anonymous"
            if caller in dependencies and callee in modules:
                dependencies[caller].append(callee)

        # 递归遍历子节点
        for child in node.get_children():
            visit_node(child)

    # 从根节点开始遍历
    visit_node(translation_unit.cursor)

    return modules, dependencies

def get_files(directory):

    cpp_files = []

    # 支持的 C++ 文件扩展名
    extensions = ["*.cpp", "*.h", "*.hpp", "*.cxx", "*.cc", "*.c"]

    # 遍历目录及其子目录
    for ext in extensions:
        cpp_files.extend(glob(os.path.join(directory, "**", ext), recursive=True))

    # 转换为绝对路径
    cpp_files = [os.path.abspath(file) for file in cpp_files]

    return cpp_files

def get_files_in_same_directory(file_path):
    # 获取文件所在目录
    directory = os.path.dirname(file_path)
    
    # 获取目录下的所有文件和文件夹
    all_items = os.listdir(directory)
    
    # 过滤出文件（排除文件夹）
    file_paths = [
        os.path.abspath(os.path.join(directory, item))
        for item in all_items
        if os.path.isfile(os.path.join(directory, item)) and item != os.path.basename(file_path)
    ]
    
    return file_paths

def build_module_dependency_graph(file_path):
    """
    解析单个 C++ 文件，构建模块依赖关系图。
    :param file_path: C++ 文件路径
    :return: 模块信息和依赖关系
    """
    index = Index.create()
    translation_unit = index.parse(file_path)

    modules = {}  # 模块名称 -> 模块信息
    dependencies = {}  # 模块名称 -> 依赖的模块列表

    def visit_node(node):
        # 提取模块（函数、类、命名空间等）
        if node.kind in [
            CursorKind.FUNCTION_DECL,  # 函数
            CursorKind.CLASS_DECL,    # 类
            CursorKind.NAMESPACE,      # 命名空间
        ]:
            module_name = node.spelling or "anonymous"
            modules[module_name] = {
                "kind": node.kind.name,
                "location": f"{node.location.file}:{node.location.line}",
            }

            # 初始化依赖关系
            if module_name not in dependencies:
                dependencies[module_name] = []

        # 提取模块之间的调用关系
        if node.kind == CursorKind.CALL_EXPR:  # 函数调用
            caller = node.semantic_parent.spelling or "anonymous"
            callee = node.referenced.spelling or "anonymous"
            if caller in dependencies and callee in modules:
                dependencies[caller].append(callee)

        # 递归遍历子节点
        for child in node.get_children():
            visit_node(child)

    visit_node(translation_unit.cursor)
    return modules, dependencies

def analyze_project(directory):
    """
    分析整个 C++ 项目，统计模块之间的关联关系数量。
    :param directory: 项目目录路径
    :return: 模块信息和依赖关系数量
    """
    cpp_files = get_files(directory)

    all_modules = {}
    all_dependencies = {}

    for file_path in cpp_files:
        modules, dependencies = build_module_dependency_graph(file_path)
        all_modules.update(modules)
        for caller, callees in dependencies.items():
            if caller not in all_dependencies:
                all_dependencies[caller] = []
            all_dependencies[caller].extend(callees)

    # 统计模块之间的调用关系数量
    dependency_counts = {}
    for caller, callees in all_dependencies.items():
        dependency_counts[caller] = len(callees)

    return all_modules, dependency_counts

def get_commit_files(commits,id,path):
    # print("path1231312313")
    # print(path)
    files={}
    for commit in commits : 
        if commit["commit"] == id:
            files=commit["files"]
    # print("11111")
    files_path=get_files(path)
    commit_files=[]
    for file in files.keys():
        f=file.replace("/","\\").split("\\")[-1]
        for file_path in files_path:
            
            if f in file_path:
                commit_files.append(file_path)
    return commit_files



# def countMC(commit_files,modules,dependency_counts):
#     mc=0
#     for name, info in modules.items():
#         if info['location'] in commit_files:
#             mc+=dependency_counts[name]
#     return mc/len(commit_files)
    
def countAC_CS(commit_files):
    ac=cs=0
    block_num=0
    comments=0
    for file in commit_files:
        code_blocks=get_code_block_comments(file)
        block_num+=len(code_blocks)
        for block in code_blocks:
            comments+=len(block['comments'])
            if len(block['comments'])!=0:
                ac+=1
                for comment,line in block["comments"].items():
                    if block['start_line']<=line<=block['end_line'] :
                        if  "//" in comment:
                            cs+=1
                    else:
                        if "/*" in comment:
                            cs+=1
    if block_num !=0 :
        ac=ac/block_num
    if comments!=0:
        cs=cs/comments
    return ac,cs

# 定义正则表达式匹配 #include 语句
INCLUDE_PATTERN = re.compile(r'#include\s+["<](.*?)[">]')

def find_cpp_files(project_dir):
    """查找项目目录中的所有 C++ 文件（.h 和 .cpp）"""
    cpp_files = []
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(('.h', '.cpp', '.c')):
                cpp_files.append(os.path.join(root, file))
    return cpp_files

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def parse_includes(file_path):
    """解析文件中的 #include 语句"""
    includes = []
    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as f:
        for line in f:
            match = INCLUDE_PATTERN.search(line)
            if match:
                includes.append(match.group(1))
    return includes

def build_dependency_graph(project_dir):
    """构建模块依赖图"""
    cpp_files = find_cpp_files(project_dir)
    dependency_graph = defaultdict(set)

    for file_path in cpp_files:
        module_name = file_path
        includes = parse_includes(file_path)
        for include in includes:
            dependency_graph[module_name].add(include)

    return dependency_graph

def count_dependencies(dependency_graph):
    """统计每个模块的依赖数量"""
    dependency_count = {}
    for module, dependencies in dependency_graph.items():
        dependency_count[module] = len(dependencies)
    return dependency_count

def analyze_project(project_dir):
    """分析整个项目并输出结果"""
    dependency_graph = build_dependency_graph(project_dir)
    dependency_count = count_dependencies(dependency_graph)

    print("模块依赖关系统计：")
    for module, count in dependency_count.items():
        print(f"{module}: {count} 个依赖")

    # 输出依赖图
    print("\n模块依赖图：")
    for module, dependencies in dependency_graph.items():
        print(f"{module} -> {', '.join(dependencies)}")

def countMC(commit_files,project_dir):
    """分析整个项目并输出结果"""
    dependency_graph = build_dependency_graph(project_dir)
    dependency_count = count_dependencies(dependency_graph)
    mc=0
    for module, count in dependency_count.items():
        if module in commit_files:
            mc+=count
        
    return mc/len(commit_files)


def countDS_C(commit_files):
    nor=ds=num=0
    c=0
    for file in commit_files:
        other_files=get_files_in_same_directory(file)
        other_files.append(file)
        encoding={}
        m=0
        for ff in other_files:
            if "CMakeList.txt" in ff or ".cmake" in ff or "CMakeList.in" in ff:
                c+=1
            with open(ff,'rb') as f:
                tmp = chardet.detect(f.read(2))
                e=tmp['encoding']
                if e in encoding.keys():
                    encoding[e]=encoding[e]+1
                    m=max(m,encoding[e])
                else:
                    encoding[e]=1
        num=len(other_files)
        nor=m
        ds+=nor/num
    return ds / len(commit_files),c/len(commit_files)

def is_file_read_only(file_path):
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 '{file_path}' 不存在")

    # 在 Windows 系统上
    if os.name == 'nt':
        # 检查文件是否可写
        return not os.access(file_path, os.W_OK)
    # 在 Unix 系统上
    else:
        # 获取文件权限
        file_mode = os.stat(file_path).st_mode
        # 检查是否没有写权限
        return not bool(file_mode & 0o200)  # 0o200 表示用户写权限

def countCM(commit_files):
    cm=0
    for file in commit_files:
        if is_file_read_only(file) == False:
            cm+=1
    return cm/len(commit_files)
mc2=cs2=1
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


# dir="E:\paper3\project\modules"
# with open("commits.json","r") as f:
#     commits=json.load(f)


# result_path="result_OpenCV4X.json"
# with open(result_path,"r") as f:
#     result=json.load(f)


# id="acc9084044438bb1de89fef83e826fd9d5e096db"
# files=get_commit_files(commits,id,dir)
# # print(files)
# # m,g=analyze_project(dir)
# ds,c=countDS_C(files)
# cm=countCM(files)
# mc=countMC(files,dir)
# ac,cs=countAC_CS(files)
# print("done")

# result["Tertiary Scores"]["Adequacy of Comments"]=ac
# result["Tertiary Scores"]["Comment Specification"]=cs
# result["Tertiary Scores"]["Code Specification"]=cs2
# result["Tertiary Scores"]["Code Modifiability"]=cm
# result["Tertiary Scores"]["Configurability"]=c
# result["Secondary Scores"]["Modular Cohesion"]=mc
# result["Tertiary Scores"]["Data Specification"]=ds
# result["Tertiary Scores"]["Modifications Complexity"]=mc2

# with open(result_path,"w+") as fp:
#     json.dump(result,fp)
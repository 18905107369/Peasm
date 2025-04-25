import json
from ahpy import Compare

# 读取用户输入的判断矩阵
def load_comparisons_from_json(file_path):
    with open(file_path, 'r') as file:
        comparisons = json.load(file)
    return comparisons

# 读取二级和三级指标的得分
def load_scores(file_path):
    with open(file_path, 'r') as file:
        scores = json.load(file)
    return scores

# 计算权重
def calculate_weights(comparisons):
    weights = {}
    for level, comparison_data in comparisons.items():
        compare = Compare(level, comparison_data, precision=3)
        print("level",level)
        print("comparison_data",comparison_data)
        print("compare.local_weights",compare.local_weights)
        weights[level] = compare.local_weights
    return weights

# 逐级加权计算最终得分
def calculate_final_score(primary_weights, secondary_weights, tertiary_weights, scores):
    final_score = 0
    for primary, primary_weight in primary_weights.items():
        primary_score = 0
        for secondary, secondary_weight in secondary_weights[primary].items():
            secondary_score = 0
            # 检查是否有三级指标
            if secondary in tertiary_weights:
                # 如果有三级指标，使用三级指标的得分加权计算
                for tertiary, tertiary_weight in tertiary_weights[secondary].items():
                    tertiary_score = scores.get(tertiary, 0)  # 从scores中获取三级指标得分
                    secondary_score += tertiary_score * tertiary_weight
            else:
                # 如果没有三级指标，直接使用二级指标的得分
                secondary_score = scores.get(secondary, 0)  # 从scores中获取二级指标得分
            primary_score += secondary_score * secondary_weight
        print(primary_weights)
        print(primary_weight)
        final_score += primary_score * primary_weight

    return final_score

# 主函数
def main():
    # 加载判断矩阵
    comparisons = load_comparisons_from_json('comparisons.json')
    
    # 计算各级权重
    primary_weights = calculate_weights(comparisons['primary'])
    # secondary_weights = calculate_weights(comparisons['secondary'])
    # tertiary_weights = calculate_weights(comparisons['tertiary'])
    
    # print("Primary Weights:", primary_weights)
    # print("Secondary Weights:", secondary_weights)
    # print("Tertiary Weights:", tertiary_weights)
    
    # # 加载二级和三级指标的得分
    # scores = load_scores('result.json')
    # # print("Scores:", scores)
    
    # # 计算最终得分
    # final_score = calculate_final_score(primary_weights, secondary_weights, tertiary_weights, scores)
    # print("Final Score:", final_score)

if __name__ == "__main__":
    main()
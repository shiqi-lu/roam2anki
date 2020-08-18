import os

import numpy as np
import pandas as pd

codename_set = {"clojure", "css", "javascript", "html"}

question_prefix = "- "
answer_prefix = "    - "

file_path = "example/code.txt"
output_path = file_path.replace(".txt", ".csv")

output = pd.DataFrame(columns=['Q', 'A'])

def block_equation(line):
    """行间公式，把前后的$$换成\[\]"""
    if line.startswith("$$") and line.endswith("$$"):
        return "\\[" + line[2:-2] + "\\]"
    else:
        return line

def inline_equation(line):
    """行内公式，把前后的$$换成\(\)"""
    if line.find("$$") == -1:
        return line
    split_list = line.split("$$")
    # 只能匹配到奇数个$$
    if len(split_list) % 2 == 0:
        return line
    for index, item in enumerate(split_list):
        if index % 2 == 1 and item:
            split_list[index] = "\\(" + item + "\\)"
    return "".join(split_list)

with open(file_path, 'r', encoding='utf-8') as f:
    Q = ""
    A = ""
    multiline_equation = False
    multiline_code = False
    for line in f.readlines():
        line = line.strip('\n')
        if not line:
            continue
        print(len(line), line)
        if line.startswith(question_prefix):
            if Q and A:
                A = "<ul>\n" + A + "\n</ul>"
                print("Q:", Q)
                print("A:", A)
                output = output.append([{'Q': Q, 'A': A}], ignore_index=True)
                A = ""
                Q = ""
            Q = inline_equation(line[len(question_prefix):])
        elif line.startswith(answer_prefix):
            line = inline_equation(block_equation(line[len(answer_prefix):]))
            # 匹配到图片
            if line.startswith("![](") and line.endswith(")"):
                line = line[4:-1]
                line = '<img src="' + line + '">'
            # 多行代码匹配开始
            if line.startswith("```"):
                line = line[3:]
                for codename in codename_set:
                    if line.startswith(codename):
                        line = line[len(codename):]
                        break
                multiline_code = True
                line = "<pre><code>" + line
                A += line
                continue
            # 多行公式匹配开始
            if line.startswith("$$"):
                multiline_equation = True
                line = "\\[" + line[2:]
            A += "<li>" + line + "</li>"
        else:
            # 答案中的多行
            # 多行代码
            if multiline_code:
                if line.endswith("```"):
                    A += "\n" + line[:-3] + "</pre></code>"
                else:
                    A += "\n" + line
                continue
            line = inline_equation(block_equation(line))
            # 多行公式匹配结束
            if multiline_equation:
                if line.endswith("$$"):
                    multiline_equation = False
                    line = line[:-2] + "\\]"
            if A.endswith("</li>"):
                A = A[:-5]
                A += "<br>"
                A += line + "</li>"
            else:
                raise Exception("can't be here, str:", line)
    else:
        A = "<ul>\n" + A + "\n</ul>"
        output = output.append([{'Q': Q, 'A': A}], ignore_index=True)

print(output)
output.to_csv(output_path, sep='\t', header=False, index=False)

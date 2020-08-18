import os
import pandas as pd

codename_set = {"clojure", "css", "javascript", "html"}

question_prefix = "- "
answer_prefix = "    - "
prefix_length = [0, 6, 10, 14, 18, 22]
answer_state_prefix = ["", "    - ", "        - ", "            - ",
                       "                - ", "                    - "]

file_path = "example/1q1a.txt"
output_path = file_path.replace(".txt", ".csv")

output = pd.DataFrame(columns=['Q', 'A'])


def is_A_empty(A):
    for item in A:
        if item:
            return False
    return True


def detect_answer_state(line, answer_state_prefix):
    i = len(answer_state_prefix) - 1
    while i >= 0:
        if line.startswith(answer_state_prefix[i]):
            return i
        i -= 1
    return 0


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
    for i, item in enumerate(split_list):
        if i % 2 == 1 and item:
            split_list[i] = "\\(" + item + "\\)"
    return "".join(split_list)


def save_A_list(A_list, output):
    index = len(A_list) - 1
    while index > 0:
        if A_list[index]:
            A_list[index - 1] += "<ul>\n" + A_list[index] + "\n</ul>"
        index -= 1

    print("Q:", Q)
    print("A:", A_list[0])
    return output.append([{'Q': Q, 'A': A_list[0]}], ignore_index=True)


with open(file_path, 'r', encoding='utf-8') as f:
    Q = ""
    # A[0]不用，A[i]对应某一级中的内容
    A_list = ["", "", "", "", "", ""]

    multiline_equation = False
    multiline_code = False
    question_state = False
    current_answer_state = -1
    previous_answer_state = -1
    for line in f.readlines():
        line = line.strip('\n')
        if not line.strip():
            continue
        print(len(line), line)
        if line.startswith(question_prefix):
            # 结束上一个答案后的保存操作
            if Q and not is_A_empty(A_list):
                output = save_A_list(A_list, output)
                Q = ""
                A_list = ["", "", "", "", "", ""]
            # 状态：开始新问题时的处理
            question_state = True
            line = line[len(question_prefix):]
            Q = inline_equation(line)
            current_answer_state = 0
            previous_answer_state = 0
            continue

        current_answer_state = detect_answer_state(line, answer_state_prefix)
        # 检测到是答案处于1~5级时
        if current_answer_state > 0:
            # 此时进入答案区
            if question_state:
                question_state = False
            # 去掉答案开头的多级格式
            line = line[prefix_length[current_answer_state]:]
            # 答案区行内，多行开始处理

            # 行内，行间公式处理
            line = inline_equation(block_equation(line))
            # 多行代码匹配开始
            # todo：取消必须占据一行的限制
            if line.startswith("```"):
                multiline_code = True
                line = line[3:]
                for codename in codename_set:
                    if line.startswith(codename):
                        line = line[len(codename):]
                        break
                line = "<pre><code>" + line
            # 匹配到图片
            # todo:得使用正则来重写，并且取消占据一整行的限制
            if line.startswith("![](") and line.endswith(")"):
                line = line[4:-1]
                line = '<img src="' + line + '">'
            # 多行行间公式匹配开始
            if line.startswith("$$"):
                multiline_equation = True
                line = "\\[" + line[2:]

            if current_answer_state >= previous_answer_state:
                # 每上升一级或平级时，在当前级别更新列表
                if multiline_code:
                    A_list[current_answer_state] += "<li>" + line
                else:
                    A_list[current_answer_state] += "<li>" + line + "</li>"
            else:
                # 级别开始下降了得对差距进行弥补，可能差不止一层
                while current_answer_state < previous_answer_state:
                    A_list[previous_answer_state - 1] += "<ul>\n" + A_list[previous_answer_state] + "\n</ul>"
                    A_list[previous_answer_state] = ""
                    previous_answer_state -= 1
                if multiline_code:
                    A_list[current_answer_state] += "<li>" + line
                else:
                    A_list[current_answer_state] += "<li>" + line + "</li>"
            previous_answer_state = current_answer_state
        else:
            # todo: 多行图片里的处理
            # todo: 支持多行里的代码块处理
            # 行内公式处理，多行里不处理行间公式
            line = inline_equation(line)
            if question_state:
                # 此时在问题区，但在多行里
                Q += "<br>" + line
            else:
                # 检测到处于0级时，此时是处于previous级答案中，但是在多行里

                # 多行代码，匹配结束与中间
                if multiline_code:
                    if line.endswith("```"):
                        A_list[previous_answer_state] += "\n" + line[:-3] + "</pre></code></li>"
                        multiline_code = False
                    else:
                        A_list[previous_answer_state] += "\n" + line
                    continue
                # 多行行间公式匹配结束
                if multiline_equation:
                    if line.endswith("$$"):
                        multiline_equation = False
                        line = line[:-2] + "\\]"
                if A_list[previous_answer_state].endswith("</li>"):
                    A_list[previous_answer_state] = A_list[previous_answer_state][:-5]
                    A_list[previous_answer_state] += "<br>"
                    A_list[previous_answer_state] += line + "</li>"
                else:
                    raise Exception("can't be here, str:", line)
    else:
        output = save_A_list(A_list, output)
        print("Q:", Q)
        print("A:", A_list[0])


print(output)
output.to_csv(output_path, sep='\t', header=False, index=False)

import os
import re
import pandas as pd

codename_set = {"clojure", "css", "javascript", "html"}

question_prefix = "- "
prefix_length = [0, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42]
answer_state_prefix = ["", " "*4+"- ", " "*8+"- ", " "*12+"- ", " "*16+"- ", " "*20+"- ",
                       " "*24+"- ", " "*28+"- ", " "*32+"- ", " "*36+"- ", " "*40+"- ",]

DOUBLE_SQUARE_BRACKET_PATTERN = r"\[\[(.*?)\]\]"
IMG_PATTERN = r"!\[(.*?)\]\((.+?)\)"
HYPERLINK_PATTERN = r"\[(.+?)\]\((.+?)\)"
BOLD_PATTERN = r"\*\*(.*?)\*\*"
ITALICS_PATTERN = r"__(.*?)__"
STRIKETHROUGHT_PATTERN = r"~~(.*?)~~"
HIGHLIGHT_PATTERN = r"\^\^(.*?)\^\^"
INLINECODE_PATTERN = r"`(.+?)`"
INLINE_EQUATION_PATTERN = r"\$\$(.*?)\$\$"

file_path = "example/all.txt"
output_path = file_path.replace(".txt", ".csv")

output = pd.DataFrame(columns=['Q', 'A'])


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
        # 若中间还存在$$说明不是行间公式
        if "$$" in line[2:-2]:
            return line
        return "\\[" + line[2:-2] + "\\]"
    else:
        return line

# todo：正则表达式匹配不了latex公式
def inline_equation1(line):
    res = re.findall(INLINE_EQUATION_PATTERN, line)
    if not res:
        return line
    newline = line
    while len(res) > 0:
        html = "\(" + res[0] + "\)"
        newline = re.sub(INLINE_EQUATION_PATTERN, html, newline, count=1)
        res = re.findall(INLINE_EQUATION_PATTERN, newline)
    return newline

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

def remove_double_square_bracket(line):
    res = re.findall(DOUBLE_SQUARE_BRACKET_PATTERN, line)
    if not res:
        return line
    newline = line
    while len(res) > 0:
        newline = re.sub(DOUBLE_SQUARE_BRACKET_PATTERN, res[0], newline, count=1)
        res = re.findall(DOUBLE_SQUARE_BRACKET_PATTERN, newline)
    return newline

def img(line):
    res = re.findall(IMG_PATTERN, line)
    if not res:
        return line
    newline = line
    while len(res) > 0:
        alt, src = res[0]
        html = f'<img src="{src}", alt="{alt}">'
        newline = re.sub(IMG_PATTERN, html, newline, count=1)
        res = re.findall(IMG_PATTERN, newline)
    return newline

def hyperlink(line):
    res = re.findall(HYPERLINK_PATTERN, line)
    if not res:
        return line
    newline = line
    while len(res) > 0:
        text, url = res[0]
        html = f'<a href="{url}">{text}</a>'
        newline = re.sub(HYPERLINK_PATTERN, html, newline, count=1)
        res = re.findall(HYPERLINK_PATTERN, newline)
    return newline

def basic_inline_format(line, PATTERN, style_name):
    res = re.findall(PATTERN, line)
    if not res:
        return line
    newline = line
    while len(res) > 0:
        content = res[0]
        html = f'<span class="{style_name}">{content}</span>'
        newline = re.sub(PATTERN, html, newline, count=1)
        res = re.findall(PATTERN, newline)
    return newline


def bold(line):
    return basic_inline_format(line, BOLD_PATTERN, "bold")


def highlight(line):
    return basic_inline_format(line, HIGHLIGHT_PATTERN, "highlight")


def strikestrough(line):
    return basic_inline_format(line, STRIKETHROUGHT_PATTERN, "strikethrough")


def inlinecode(line):
    return basic_inline_format(line, INLINECODE_PATTERN, "inlinecode")


def italics(line):
    return basic_inline_format(line, ITALICS_PATTERN, "italic")

def all_inline_format(line):
    return italics(inlinecode(strikestrough(highlight(bold(hyperlink(img(line)))))))

def is_A_empty(A):
    for item in A:
        if item:
            return False
    return True


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
            # 匹配行内格式
            line = all_inline_format(line)
            # 匹配到行内公式
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

            # 多行行间公式匹配开始
            if line.startswith("$$"):
                multiline_equation = True
                line = "\\[" + line[2:]

            # 仅在非多行公式和非多行代码才匹配所有行内格式
            if not multiline_code and not multiline_equation:
                line = all_inline_format(line)

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
            # todo: 支持多行里的代码块处理
            # 行内公式处理，多行里不处理行间公式
            line = inline_equation(line)
            if not multiline_code and not multiline_equation:
                line = all_inline_format(line)
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

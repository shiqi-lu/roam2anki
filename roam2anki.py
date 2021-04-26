import os
import sys
import re
import html
import pandas as pd

question_prefix = "- "
prefix_length = [0, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42]
answer_state_prefix = ["", " " * 4 + "- ", " " * 8 + "- ", " " * 12 + "- ", " " * 16 + "- ", " " * 20 + "- ",
                       " " * 24 + "- ", " " * 28 + "- ", " " * 32 + "- ", " " * 36 + "- ", " " * 40 + "- ", ]

DOUBLE_SQUARE_BRACKET_PATTERN = r"\[\[(.*?)\]\]"
IMG_PATTERN = r'(&quot;)?!\[(.*?)\]\((.+?)\)(&quot;)?'
HYPERLINK_PATTERN = r"\[(.+?)\]\((.+?)\)"
BOLD_PATTERN = r"\*\*(.*?)\*\*"
ITALICS_PATTERN = r"__(.*?)__"
STRIKETHROUGHT_PATTERN = r"~~(.*?)~~"
HIGHLIGHT_PATTERN = r"\^\^(.*?)\^\^"
INLINECODE_PATTERN = r"`(.+?)`"
INLINE_EQUATION_PATTERN = r"\$\$(.*?)\$\$"
ALIAS_PATTERN = r"{{alias:\s*\[\[.*\]\]\s*(.*?)}}"

# 强制选择代码格式：
# inherit表示直接继承自```后面定义的
# 其它的都强制写入
codeblock_format = "inherit"


def detect_answer_state(line, answer_state_prefix):
    i = len(answer_state_prefix) - 1
    while i >= 0:
        if line.startswith(answer_state_prefix[i]):
            return i
        i -= 1
    return 0


def block_equation(line):
    """行间公式，把前后的$$换成\[\]"""
    if len(line) <= 4:
        return line
    if line.startswith("$$") and line.endswith("$$"):
        # 若中间还存在$$说明不是行间公式
        if "$$" in line[2:-2]:
            return line
        return "\\[" + line[2:-2] + "\\]"
    elif line.startswith('"$$') and line.endswith('$$"'):
        # 支持引用的行间公式
        if "$$" in line[3:-3]:
            return line
        return "\\[" + line[3:-3] + "\\]"
    else:
        return line


# 正则表达式匹配不了latex公式
def inline_equation1(line):
    res = re.findall(INLINE_EQUATION_PATTERN, line)
    if not res:
        return line
    while len(res) > 0:
        html = "\(" + res[0] + "\)"
        line = re.sub(INLINE_EQUATION_PATTERN, html, line, count=1)
        res = re.findall(INLINE_EQUATION_PATTERN, line)
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


def remove_double_square_bracket(line):
    res = re.findall(DOUBLE_SQUARE_BRACKET_PATTERN, line)
    if not res:
        return line
    while len(res) > 0:
        line = re.sub(DOUBLE_SQUARE_BRACKET_PATTERN, res[0], line, count=1)
        res = re.findall(DOUBLE_SQUARE_BRACKET_PATTERN, line)
    return line


def img(line):
    res = re.findall(IMG_PATTERN, line)
    if not res:
        return line
    while len(res) > 0:
        html = f'<div style="text-align: center;"><img src="{res[0][2]}", alt="{res[0][1]}"></div>'
        line = re.sub(IMG_PATTERN, html, line, count=1)
        res = re.findall(IMG_PATTERN, line)
    return line


def hyperlink(line):
    res = re.findall(HYPERLINK_PATTERN, line)
    if not res:
        return line
    while len(res) > 0:
        text, url = res[0]
        html = f'<a href="{url}">{text}</a>'
        line = re.sub(HYPERLINK_PATTERN, html, line, count=1)
        res = re.findall(HYPERLINK_PATTERN, line)
    return line


def alias(line):
    res = re.findall(ALIAS_PATTERN, line)
    if not res:
        return line
    while len(res) > 0:
        line = re.sub(ALIAS_PATTERN, res[0], line, count=1)
        res = re.findall(ALIAS_PATTERN, line)
    return line


def basic_inline_format(line, PATTERN, style_name):
    res = re.findall(PATTERN, line)
    if not res:
        return line
    while len(res) > 0:
        content = res[0]
        html = f'<span class="{style_name}">{content}</span>'
        line = re.sub(PATTERN, html, line, count=1)
        res = re.findall(PATTERN, line)
    return line


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
    return remove_double_square_bracket(alias(
        italics(inlinecode(strikestrough(highlight(bold(hyperlink(img(line)))))))))


def code_block_start(line):
    codename = line.strip()
    html_start = ""
    if codeblock_format == "inherit":
        html_start = f'<pre><code class="{codename}">'
    else:
        html_start = f'<pre><code class="{codeblock_format}">'
    return html_start


def is_A_empty(A):
    for item in A:
        if item:
            return False
    return True


def save_A_list(Q, A_list, output):
    index = len(A_list) - 1
    while index > 0:
        if A_list[index]:
            A_list[index - 1] += "<ul>\n" + A_list[index] + "\n</ul>"
        index -= 1

    # print("Q:", Q)
    # print("A:", A_list[0])
    return output.append([{'Q': Q, 'A': A_list[0]}], ignore_index=True)


def main(file_path):
    output_path = file_path.replace(".txt", ".csv")
    output = pd.DataFrame(columns=['Q', 'A'])
    with open(file_path, 'r', encoding='utf-8') as f:
        Q = ""
        # A[i]对应某一级中的内容
        # 其中A[0]不用，仅在要保存答案的时候逐级把后面内容合并到A[0]，A[0]为最终答案
        A_list = [""] * 11

        multiline_equation = False
        multiline_code_first_line = False
        multiline_code = False
        question_state = False
        current_answer_state = 0
        previous_answer_state = 0
        h1 = False
        h2 = False
        h3 = False
        for line in f.readlines():
            line = line.strip('\n')
            if not line.strip():
                continue
            # print(len(line), line)
            if line.startswith(question_prefix):
                # 结束上一个答案后的保存操作
                if Q and not question_state:
                    output = save_A_list(Q, A_list, output)
                    Q = ""
                    A_list = [""] * 11
                    multiline_equation = False
                    multiline_code = False
                    multiline_code_first_line = False
                # 状态：开始新问题时的处理

                h1 = False
                h2 = False
                h3 = False
                line = line[len(question_prefix):]
                if not line.strip():
                    continue
                if line.startswith("```"):
                    multiline_code = True
                    multiline_code_first_line = True
                    line = line[3:]
                    Q += code_block_start(line)
                elif line.startswith("$$") and "$$" not in line[2:]:
                    # 多行行间公式匹配开始
                    multiline_equation = True
                    Q += "\\[" + html.escape(line[2:])
                else:
                    # 仅在非代码块时匹配行内格式
                    line = inline_equation(block_equation(line))
                    line = html.escape(line)
                    line = all_inline_format(line)
                    if question_state:
                        Q += "<br>"
                    if line.startswith("# "):
                        Q += "<h1>" + line[2:] + "</h1>"
                        h1 = True
                    elif line.startswith("## "):
                        Q += "<h2>" + line[3:] + "</h2>"
                        h2 = True
                    elif line.startswith("### "):
                        Q += "<h3>" + line[4:] + "</h3>"
                        h3 = True
                    else:
                        Q += line
                question_state = True
                current_answer_state = 0
                previous_answer_state = 0
                continue

            current_answer_state = detect_answer_state(line, answer_state_prefix)
            # 检测到是答案处于1~5级时
            if current_answer_state > 0:
                # 此时进入答案区
                h1 = False
                h2 = False
                h3 = False
                if question_state:
                    question_state = False
                # 去掉答案开头的多级格式
                line = line[prefix_length[current_answer_state]:]
                if not line.strip():
                    continue
                # 答案区行内，多行开始处理

                # 行间公式处理
                line = block_equation(line)
                # 多行代码匹配开始
                # todo：取消必须占据一行的限制
                if line.startswith("```"):
                    multiline_code = True
                    multiline_code_first_line = True
                    line = line[3:]
                    line = code_block_start(line)
                elif line.startswith("$$") and "$$" not in line[2:]:
                    # 多行行间公式匹配开始
                    multiline_equation = True
                    line = "\\[" + html.escape(line[2:])
                elif not multiline_code and not multiline_equation:
                    # 仅在非多行公式和非多行代码才匹配所有行内格式
                    line = inline_equation(line)
                    line = html.escape(line)
                    line = all_inline_format(line)
                    if line.startswith("# "):
                        line = "<h1>" + line[2:] + "</h1>"
                        h1 = True
                    elif line.startswith("## "):
                        line = "<h2>" + line[3:] + "</h2>"
                        h2 = True
                    elif line.startswith("### "):
                        line = "<h3>" + line[4:] + "</h3>"
                        h3 = True
                else:
                    line = html.escape(line)

                if current_answer_state > previous_answer_state:
                    # 每上升一级时，在当前级别更新列表
                    if multiline_code:
                        A_list[current_answer_state] += "<li>" + line
                    else:
                        A_list[current_answer_state] += "<li>" + line + "</li>"
                elif current_answer_state > previous_answer_state:
                    # 平级时，在当前级别更新列表
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
                if not multiline_code and line.startswith("```"):
                    multiline_code = True
                    multiline_code_first_line = True
                    line = line[3:]
                    line = code_block_start(line)
                    if question_state:
                        Q += line
                    else:
                        A_list[previous_answer_state] += line
                    continue
                elif not multiline_equation and line.startswith("$$") and "$$" not in line[2:]:
                    # 多行行间公式匹配开始
                    multiline_equation = True
                    line = "\\[" + html.escape(line[2:])
                    if question_state:
                        Q += line
                    else:
                        A_list[previous_answer_state] += line
                    continue
                if question_state:
                    # 此时在问题区，但在多行里
                    if multiline_code:
                        if line.endswith("```"):
                            if multiline_code_first_line:
                                Q += html.escape(line[:-3]) + "</pre></code>"
                                multiline_code_first_line = False
                            else:
                                Q += "\n" + html.escape(line[:-3]) + "</pre></code>"
                            multiline_code = False
                        else:
                            if multiline_code_first_line:
                                Q += html.escape(line)
                                multiline_code_first_line = False
                            else:
                                Q += "\n" + html.escape(line)
                    elif multiline_equation:
                        if line.endswith("$$"):
                            multiline_equation = False
                            Q += html.escape(line[:-2]) + "\\]"
                        else:
                            Q += "<br>" + html.escape(line)
                    else:
                        # 行内公式处理
                        line = inline_equation(block_equation(line))
                        line = html.escape(line)
                        line = all_inline_format(line)
                        if h1:
                            Q += "<br>" + line[:-5] + "</h1>"
                        elif h2:
                            Q += "<br>" + line[:-5] + "</h2>"
                        elif h3:
                            Q += "<br>" + line[:-5] + "</h3>"
                        else:
                            Q += "<br>" + line
                else:
                    # 检测到处于0级时，此时是处于previous级答案中，但是在多行里

                    # 多行代码，匹配结束与中间
                    if multiline_code:
                        if line.endswith("```"):
                            if multiline_code_first_line:
                                A_list[previous_answer_state] += html.escape(line[:-3]) + "</pre></code></li>"
                                multiline_code_first_line = False
                            else:
                                A_list[previous_answer_state] += "\n" + html.escape(line[:-3]) + "</pre></code></li>"
                            multiline_code = False
                        else:
                            if multiline_code_first_line:
                                A_list[previous_answer_state] += html.escape(line)
                                multiline_code_first_line = False
                            else:
                                A_list[previous_answer_state] += "\n" + html.escape(line)
                        continue
                    # 多行行间公式匹配结束
                    elif multiline_equation:
                        if line.endswith("$$"):
                            multiline_equation = False
                            line = html.escape(line[:-2]) + "\\]"
                        else:
                            line = html.escape(line)
                    else:
                        # 行内公式处理
                        line = inline_equation(block_equation(line))
                        line = html.escape(line)
                        line = all_inline_format(line)
                    if A_list[previous_answer_state].endswith("</li>"):
                        A_list[previous_answer_state] = A_list[previous_answer_state][:-5]
                        if h1 or h2 or h3:
                            A_list[previous_answer_state] = A_list[previous_answer_state][:-5]
                        A_list[previous_answer_state] += "<br>"
                        A_list[previous_answer_state] += line
                        if h1:
                            A_list[previous_answer_state] += "</h1>"
                        elif h2:
                            A_list[previous_answer_state] += "</h2>"
                        elif h3:
                            A_list[previous_answer_state] += "</h3>"
                        A_list[previous_answer_state] += "</li>"
                    else:
                        raise Exception("can't be here, str:", line)
        else:
            # 结束，最后一组问答要保存一下
            output = save_A_list(Q, A_list, output)

    # print(output)
    output.to_csv(output_path, sep='\t', header=False, index=False)

    # 因为一行开头如果是#那么导入的时候会被忽略，所以，不想改源代码了，
    # 以后有空用有限状态机改一波，现在直接操作文件，在#开头的前面加个空格吧
    fr = open(output_path, "r")
    fw = open(f"{output_path}.csv", "w")
    for line in fr.readlines():
        if line.startswith("#"):
            line = " " + line
        fw.write(line)

    fr.close()
    fw.close()
    os.rename(f"{output_path}.csv", output_path)


def print_help_and_exit():
    print("Usage: python roam2anki.py FILE/DIR ...")
    exit(1)


if __name__ == '__main__':
    # main("example/example.txt")
    # exit(0)
    if len(sys.argv) == 1:
        print_help_and_exit()

    for path in sys.argv[1:]:
        if not os.path.exists(path):
            print(path, "not exists")
            print_help_and_exit()
        if os.path.isfile(path):
            if not path.endswith(".txt"):
                print_help_and_exit()
            main(path)
        elif os.path.isdir(path):
            for filename in os.listdir(path):
                full_path = os.path.join(path, filename)
                if os.path.isfile(full_path) and full_path.endswith(".txt"):
                    main(full_path)
        else:
            print(path, "not exists")
            print_help_and_exit()

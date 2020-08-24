# roam2anki
roam2anki用来把roam的笔记转成anki进行记忆

# 介绍
已经完成所有规划的功能，已支持roam中的所有样式，包括行内、行间公式、代码块、高亮、加粗、图片、超链接等等，其中第一级会解析为问题，第二级和往后级别均解析为第一级的答案

# 用法
1. 下载roam2anki.py和roam2anki模板.apkg
2. 第一次操作先在anki中导入roam2anki模板.apkg
3. 新建一个txt文件如example.txt，把要导入的roam字段粘贴到文本中，注意第一级为问题，第二级以下都是答案
4. 运行python脚本`python roam2anki.py example.txt`，程序把转换成对应的只有两列的csv文件，问题是第一列，回答是第二列
5. 把csv导入到anki中，保持默认设置即可。即fields separated by: Tab；勾选上Allow HTML in fields；Field 1为正面；field 2为背面

# 功能列表
* [x] 只支持普通的文字的导入一个问题，且只有一个回答
* [x] 支持普通文字导入一个问题，有多个回答
* [x] 支持普通文字导入多个问题
* [x] 支持导入一个块内的多行内容
* [x] 支持公式的导入
* [x] 行内公式转换成\( \)
* [x] 行间公式转换成\[ \]
* [x] 需要先验证anki是否支持多行公式
* [x] 多行行间公式
* [x] 支持代码块的最简单的导入
* [x] 支持图片格式的转换
* [x] 问题支持块内多行
* [x] 代码高亮：需要学习模板的内如何嵌入js和css，并作为资源本地同步
* [x] 支持删字符
* [x] 支持高亮格式
* [x] 支持行内代码
* [x] 支持加粗
* [x] 支持斜体
* [x] 支持超链接
* [x] 级别可提升到10级
* [x] 删除一行中的页面跳转符号
* [x] 代码块高亮格式的额外选择
* [x] 支持标题字号h1到h3
* [x] 支持问题中的代码块
* [x] 问题区支持行间公式
* [x] 支持引用的行间公式和代码块
* [x] 问题区把连续的一级块组合成同一个问题

# 限制
- 答案内的代码块必须要新起一个块或新起一行，且这一行必须以3个反引号开始
- 问题内的代码块必须新起一行，且这一行必须以3个反引号开始
- 暂时只支持无序列表，不支持有序列表和文档

# 其它说明
- roam2anki只支持语法正确时的解析，即保证在roam中能正确解析的，导出anki后也正确解析，不正确的语法，或故意为难解析器的，，我也没办法哇
- roam2anki使用python3.7写成，仅使用了pandas库，若没有安装pandas，运行`pip install pandas`即可 
- roam2anki.py提供了批量转换的方法，第二个选项`python roam2anki.py example`，若example为一个文件夹，会寻找example下的所有以.txt结尾的文件进行转换
- 目前roam支持的代码块中高亮格式非常有限，只有css、html、clojure、javascript四种，所以roam2anki.py中提供了一个选项，可以强制更改代码块的高亮语法，即`python roam2anki.py example/code.txt python`，在程序后面新增一个字段，如python，cpp，java等，可以设定导出的anki卡片中的代码高亮语法规则
- roam2anki目前是作者写给自用，若使用过程中发现有解析出来的bug，请提一个issue

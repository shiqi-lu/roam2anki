# roam2anki
roam2anki用来把roam的笔记转成anki进行记忆

目前只支持两级，第一级是问题，第二级是答案，基本功能已经完备了，可以导出支持代码，公式等
后续功能有空再开发

# 用法
  - 把roam字段粘贴到文本中，第一层是问题，第二层以下都是答案
  - 使用python脚本转换成对应的csv文件，问题是第一列，回答是第二列
  - 把csv导入到anki中


# Roadmap
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
* [ ] 支持问题回答中是多级嵌套
* [ ] 代码高亮：需要学习模板的内如何嵌入js和css，并作为资源本地同步
* [ ] 支持高亮格式
* [ ] 支持行内代码
* [ ] 支持加粗
* [ ] 支持斜体
* [ ] 支持删字符
* [ ] 删除一行中的页面跳转符号
* [ ] 支持超链接
* [ ] 支持标题字号h1到h3
* [ ] 问题支持块内多行

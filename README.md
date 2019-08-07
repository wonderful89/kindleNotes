## 项目说明

这是一个使用 python 语言编写的项目，用于将 kindle 笔记导出为网页文件。
本项目模仿自[cyang812](https://github.com/cyang812/kindleNote)。

## 使用说明

### 生成网页
- 1、从 kindle 中拷贝出标注文件，My Clippings.txt。
- 2、在 Python3 环境下执行 `python demo.py` 指令，等待生成网页文件。
（如果报错`TypeError: 'encoding' is an invalid keyword argument for this function`,需要执行 `python3 demo.py` 指令）


### 生成 `markdown` 文件

- 1、从 kindle 中拷贝出标注文件，My Clippings.txt。
- 2、在 Python3 环境下执行 `python markdown.py` 指令，等待out文件夹中生成文件。
（如果报错`TypeError: 'encoding' is an invalid keyword argument for this function`,需要执行 `python3 demo.py` 指令）


## TODO

1. 按照章节，先后排序
2. 统计总数
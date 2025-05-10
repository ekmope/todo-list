<!-- markdownlint-disable first-line-h1 -->
<!-- markdownlint-disable html -->
<!-- markdownlint-disable no-duplicate-header -->

<div align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/3293/3293464.png" width="20%" alt="Todo List" />
</div>
<hr>
<div align="center" style="line-height: 1;">
  <a href="https://github.com/ekmope/todo-list"><img alt="GitHub Repo"
    src="https://img.shields.io/badge/📂%20GitHub-Todo_List-536af5?logo=github&color=536af5"/></a>
  <a href="https://choosealicense.com/licenses/mit/"><img alt="License"
    src="https://img.shields.io/badge/📜%20License-MIT-f5de53?color=f5de53"/></a>
  <a href="https://pypi.org/project/pyinstaller/"><img alt="PyInstaller"
    src="https://img.shields.io/badge/📦%20Packaged_with-PyInstaller-2ba97a?color=2ba97a"/></a>
</div>

## Table of Contents

1. [Introduction](#1-introduction)  
2. [Features](#2-features)  
3. [Quick Start](#3-quick-start)  
4. [Advanced Usage](#4-advanced-usage)  
5. [Build from Source](#5-build-from-source)  
6. [Roadmap](#6-roadmap)  
7. [Contributing](#7-contributing)  

---

## 1. Introduction

**Todo List** 是一个轻量级命令行任务管理工具，支持跨平台运行（Windows/macOS/Linux）。通过简洁的命令交互实现高效任务管理，数据自动持久化存储，适合开发者和终端用户日常使用。

<div align="center">
  <img src="demo.gif" width="70%">
</div>

---

## 2. Features

### Core Architecture
- **极简设计**：单文件实现核心逻辑（<200行代码）
- **数据持久化**：自动保存任务到 `todo.txt` 文件
- **跨平台兼容**：完美支持 Windows CMD/PowerShell 和 Unix Shell

### Functional Highlights
- ✅ 添加/删除/完成任务  
- ✅ 任务状态可视化（[ ]未完成 vs [x]已完成）  
- ✅ 数据自动保存与加载  
- 🚀 支持打包为独立可执行文件（.exe/.app）  

---

## 3. Quick Start

### Prerequisites
- Python 3.6+  
- Git（可选）

### Installation
```bash
# Clone 仓库
git clone https://github.com/ekmope/todo-list.git
cd todo-list

# 直接运行
python todo.py
Basic Commands
Command	Description	Example
add	添加任务	add 购买牛奶
done	标记完成	done 2
list	查看任务列表	list
clear	清空所有任务	clear
exit	退出程序	exit
## 4. Advanced Usage
数据文件定制
修改 TODO_FILE 变量指定存储路径：

python
# 在 todo.py 中修改
TODO_FILE = "/path/to/custom_tasks.txt"
日志记录（示例扩展）
python
import logging
logging.basicConfig(filename='todo.log', level=logging.INFO)
## 5. Build from Source
生成可执行文件
bash
# 安装依赖
pip install pyinstaller

# 打包（Windows）
pyinstaller --onefile --name todo.exe todo.py

# 打包（macOS/Linux）
pyinstaller --onefile --name todo todo.py
输出路径
dist/
  ├── todo.exe    # Windows可执行文件
  └── todo        # Unix可执行文件
## 6. Roadmap
状态	功能	目标版本
✅	基础任务管理	v1.0
🚧	任务分类标签	v1.2
⏳	云端同步功能	v2.0
⏳	图形界面（Tkinter）	v2.1
## 7. Contributing
欢迎通过以下方式参与贡献：

Fork 本仓库

创建功能分支 (git checkout -b feature/awesome)

提交修改 (git commit -am 'Add awesome feature')

推送分支 (git push origin feature/awesome)

发起 Pull Request
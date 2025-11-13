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
6. [Contributing](#6-contributing)
7. [License](#7-license)
8. [Contact](#8-contact)

---

## 1. Introduction

**Todo List** 是一个轻量级命令行任务管理工具，支持跨平台运行 (Windows/macOS/Linux)   通过简洁的命令交互实现高效任务管理，数据自动持久化存储，适合开发者和终端用户日常使用。

<div align="center">
  <img src="demo.gif" width="70%">
</div>

---

## 2. Features

### Core Architecture

* ✨ 极简设计：单文件实现核心逻辑
* 📂 数据持久化：自动保存任务到 `~/.todo.json`
* 🚀 自动备份：自动创建最多 5 份 JSON 备份
* ☑️ 事件高亮：支持任务优先级分色标记

### Functional Highlights

* ✅ 添加/删除/完成/修改/搜索 任务
* ✅ 任务状态可视化 ( □ vs ✓ )
* ✅ 支持多运行平台 + 类 Unix 色彩输出
* ✅ 合理错误处理，防止数据损坏

---

## 3. Quick Start

### Prerequisites

* Python 3.6+

### Installation

```bash
# Clone 仓库
$ git clone https://github.com/ekmope/todo-list.git
$ cd todo-list

# 直接运行
$ python todo4.0.py
```

### Basic Commands

| Command  | Description | Example        |
| -------- | ----------- | -------------- |
| `add`    | 添加任务        | `add 购买牛奶`     |
| `done`   | 标记完成        | `done 2`       |
| `edit`   | 编辑任务        | `edit 2 购买美容罐` |
| `remove` | 删除指定任务      | `remove 1`     |
| `clear`  | 清空所有任务      | `clear`        |
| `list`   | 显示任务列表      | `list`         |
| `search` | 搜索包含关键词任务   | `search 牛奶`    |
| `exit`   | 退出程序        | `exit`         |

---

## 4. Advanced Usage

### 自定义任务文件路径

在源码中修改:

```python
TODO_FILE = Path.home() / ".todo.json"
```

### 数据备份

每次读取数据时会自动备份到 `~/todo_backups/`，最多保留 5 份，高效防止损坏。

---

## 5. Build from Source

### 生成可执行文件

```bash
# 安装打包工具
pip install pyinstaller

# Windows 打包
pyinstaller --onefile --name todo.exe todo4.0.py

# macOS/Linux 打包
pyinstaller --onefile --name todo todo4.0.py
```

### 输出文件

```
dist/
  ├── todo.exe    # Windows
  └── todo        # Unix/macOS
```

---

## 6. Contributing

欢迎不同方式的贡献：

1. Fork 本项目
2. 创建分支 
3. 提交修改 
4. 推送分支 
5. 发起 Pull Request

---

## 7. License

本项目采用 [MIT License](LICENSE)，允许商业使用和修改：

* 须保留版权声明
* 未提供任何报保或报价

---

## 8. Contact

遇到问题或有好事情想跟我说？
If you encounter problems or have good things to tell me

* 🛏 Email: [2014036853@qq.com](mailto:2014036853@qq.com)
* 🐛 [Issue Tracker](https://github.com/ekmope/todo-list/issues)

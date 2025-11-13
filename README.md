<div align="center"><img src="https://cdn-icons-png.flaticon.com/512/3293/3293464.png" width="20%" alt="Todo List" /></div>
<hr>
<div align="center" style="line-height: 1;"><a href="https://github.com/ekmope/todo-list"><img alt="GitHub Repo"src="https://img.shields.io/badge/📂%20GitHub-Todo_List-536af5?logo=github&color=536af5"/></a><a href="https://choosealicense.com/licenses/mit/"><img alt="License"src="https://img.shields.io/badge/📜%20License-MIT-f5de53?color=f5de53"/></a><a href="https://pypi.org/project/pyinstaller/"><img alt="PyInstaller"src="https://img.shields.io/badge/📦%20Packaged_with-PyInstaller-2ba97a?color=2ba97a"/></a></div>
Table of Contents
Introduction
Features
Quick Start
Advanced Usage
Build from Source
Contributing
License
Contact
1. Introduction
Todo List 是一个轻量级命令行任务管理工具，支持跨平台运行 (Windows/macOS/Linux) 通过简洁的命令交互实现高效任务管理，数据自动持久化存储，适合开发者和终端用户日常使用。当前版本：v5.3
<div align="center"><img src="demo.gif" width="70%"></div>
2. Features
Core Architecture
✨ 极简设计：单文件实现核心逻辑
📂 数据持久化：自动保存任务到 ~/.todo.json
🚀 自动备份：自动创建最多 5 份 JSON 备份
☑️ 事件高亮：支持任务优先级分色标记、过期任务标红
Functional Highlights
✅ 添加 / 删除 / 完成 / 修改 / 搜索 任务
✅ 任务状态可视化 (□ vs ✓)
✅ 支持多运行平台 + 类 Unix 色彩输出
✅ 合理错误处理，防止数据损坏
✅ 支持任务截止日期设置（多种格式：YYYY-MM-DD HH:MM、today、tomorrow、3days 等）
✅ 任务统计功能（含总任务数、完成率、优先级分布、今日 / 本周新增与完成数等）
✅ 启动时自动提醒过期任务
✅ 支持按截止日期排序查看任务列表
3. Quick Start
Prerequisites
Python 3.6+
Installation
bash
# Clone 仓库
$ git clone https://github.com/ekmope/todo-list.git
$ cd todo-list

# 直接运行
$ python todo_0.5.3.py
Basic Commands
Command	Description	Example
add/a	添加任务（支持 --priority 设置优先级，--due 设置截止日期）	add 购买牛奶 --priority high --due tomorrow a 写报告 --due 2024-12-31
done/d	标记任务为完成	done 2 d 3
edit/e	编辑任务（支持 --priority 修改优先级，--due 修改截止日期，输入 'none' 清除截止日期）	edit 2 --due none 购买酸奶 e 3 --priority low
remove/r	删除指定任务	remove 1 r 4
clear/c	清空所有任务	clear c
list/l	显示任务列表（--due 按截止日期排序）	list l --due
search/s	搜索包含关键词任务	search 牛奶 s 报告
stats/st	查看任务统计数据（含时间维度）	stats st
exit	退出程序	exit
4. Advanced Usage
自定义任务文件路径
在源码中修改:
python
运行
TODO_FILE = Path.home() / ".todo.json"
数据备份
每次读取数据时会自动备份到 ~/todo_backups/，最多保留 5 份，高效防止损坏。
5. Build from Source
生成可执行文件
bash
# 安装打包工具
pip install pyinstaller

# Windows 打包
pyinstaller --onefile --name todo.exe todo_0.5.3.py

# macOS/Linux 打包
pyinstaller --onefile --name todo todo_0.5.3.py
输出文件
plaintext
dist/
  ├── todo.exe    # Windows
  └── todo        # Unix/macOS
6. Contributing
欢迎不同方式的贡献：
Fork 本项目
创建分支
提交修改
推送分支
发起 Pull Request
7. License
本项目采用 MIT License，允许商业使用和修改：
须保留版权声明
未提供任何报保或报价
8. Contact
遇到问题或有好事情想跟我说？If you encounter problems or have good things to tell me
🛏 Email: 2014036853@qq.com
🐛 Issue Tracker
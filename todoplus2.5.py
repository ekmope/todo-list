"""
命令行Todo List管理系统 - 增强版
版本：2.5
更新内容：
- 修复编辑命令内容为空问题
- 支持灵活的参数位置解析
- 增强时间显示对齐
- 明确JSON解码错误处理
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from functools import wraps

# ====================
#    配置项
# ====================
TODO_FILE = Path.home() / ".todo.json"
COLOR_ENABLED = True
DATE_FORMAT = "%Y-%m-%d %H:%M"
PRIORITY_COLORS = {
    "high": "red",
    "normal": "yellow",
    "low": "blue"
}
VALID_PRIORITIES = list(PRIORITY_COLORS.keys())

# ====================
#    颜色支持
# ====================
if COLOR_ENABLED and sys.platform == "win32":
    os.system("color")

COLOR_MAP = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "reset": "\033[0m"
}

def color_text(text, color):
    return f"{COLOR_MAP[color]}{text}{COLOR_MAP['reset']}" if COLOR_ENABLED else text

def print_color(text, color):
    print(color_text(text, color))

# ====================
#    核心逻辑
# ====================
class TodoManager:
    def __init__(self):
        self.tasks = self._load_tasks()
        self.next_id = self._get_next_id()

    def _load_tasks(self):
        try:
            if not TODO_FILE.exists():
                return []
            
            with open(TODO_FILE, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    raise ValueError("任务文件损坏，已重置")
                
                if not isinstance(data, list):
                    raise ValueError("数据格式错误，已重置")
                return data
        except Exception as e:
            self._show_error(f"加载失败: {str(e)}")
            # 创建新文件防止后续操作失败
            with open(TODO_FILE, "w") as f:
                json.dump([], f)
            return []

    def _get_next_id(self):
        if not self.tasks:
            return 1
        existing_ids = {t["id"] for t in self.tasks if "id" in t}
        return max(existing_ids) + 1 if existing_ids else 1

    def edit_task(self, task_id, new_content, new_priority=None):
        task = self._find_task(task_id)
        if not task:
            return False
        
        task["content"] = new_content
        if new_priority:
            if new_priority not in VALID_PRIORITIES:
                self._show_error(f"无效优先级: {new_priority}")
                return False
            task["priority"] = new_priority
        task["modified"] = datetime.now().strftime(DATE_FORMAT)
        return self._save_tasks()

    # ...（其他方法保持不变）...

# ====================
#    增强型参数解析
# ====================
@command_handler
def handle_edit(manager, args):
    if len(args) < 2 or not args[0].isdigit():
        raise ValueError("格式: edit <编号> [--priority 级别] <新内容>")
    
    task_id = int(args[0])
    new_priority = None
    content_args = []
    priority_specified = False

    # 灵活解析--priority参数位置
    i = 1
    while i < len(args):
        if args[i] == "--priority":
            if i+1 >= len(args):
                raise ValueError("需要指定优先级级别")
            new_priority = args[i+1].lower()
            if new_priority not in VALID_PRIORITIES:
                raise ValueError(f"优先级必须是 {', '.join(VALID_PRIORITIES)}")
            i += 2  # 跳过已处理参数
            priority_specified = True
        else:
            content_args.append(args[i])
            i += 1
    
    new_content = " ".join(content_args)
    if not new_content and not priority_specified:
        raise ValueError("必须提供新内容或修改优先级")
    
    if manager.edit_task(task_id, new_content, new_priority):
        print_color(f"✓ 任务 {task_id} 已修改", "green")

# ====================
#    优化时间显示对齐
# ====================
@command_handler
def handle_list(manager, args):
    # ...（过滤逻辑保持不变）...
    
    # 表头（固定宽度）
    header = color_text(
        f"{'ID':<4} {'状态':<3} {'优先级':<6} {'创建时间':<19} {'修改时间':<19} 内容",
        "yellow"
    )
    print(header)
    
    for task in filtered:
        status_icon = color_text("✓", "green") if task["status"] == "done" else color_text("◻", "red")
        pri_color = PRIORITY_COLORS.get(task["priority"], "yellow")
        pri_mark = color_text("◆", pri_color)
        
        # 统一时间显示宽度
        created_time = color_text(task['created'], "blue").ljust(19)
        modified_time = color_text(
            task['modified'] if task['modified'] != task['created'] else "-",
            "blue"
        ).ljust(19)
        
        print(f"#{task['id']:<3} {status_icon} {pri_mark:<2} {created_time} {modified_time} {task['content']}")

# ====================
#    增强错误处理
# ====================
def _show_error(self, message):
    print_color(f"✗ {message}（输入help查看帮助）", "red")

# ...（其他函数保持不变）...

if __name__ == "__main__":
    main()
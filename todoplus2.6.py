"""
命令行Todo List管理系统 - 增强版
版本：2.6
更新内容：
- 修复编辑任务内容保留问题
- 增加数据文件损坏自动备份
- 优化时间动态对齐显示
- 完善帮助文档
"""

import os
import sys
import json
import shutil
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
#    核心逻辑（关键改进）
# ====================
class TodoManager:
    def __init__(self):
        self.tasks = self._load_tasks()
        self.next_id = self._get_next_id()

    def _load_tasks(self):
        try:
            if not TODO_FILE.exists():
                return []

            # 创建备份副本
            backup_path = TODO_FILE.with_suffix('.json.bak')
            shutil.copyfile(TODO_FILE, backup_path)

            with open(TODO_FILE, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    raise ValueError(f"文件损坏，备份已保存至 {backup_path}")
                
                if not isinstance(data, list):
                    raise ValueError(f"数据格式错误，备份已保存至 {backup_path}")
                return data
        except Exception as e:
            self._show_error(f"加载失败: {str(e)}")
            # 创建新文件防止后续操作失败
            with open(TODO_FILE, "w") as f:
                json.dump([], f)
            return []

    def edit_task(self, task_id, new_content, new_priority=None):
        task = self._find_task(task_id)
        if not task:
            return False
        
        # 保留原内容如果新内容为空
        if new_content is None:
            new_content = task["content"]
        
        task["content"] = new_content
        if new_priority:
            if new_priority not in VALID_PRIORITIES:
                self._show_error(f"无效优先级: {new_priority}")
                return False
            task["priority"] = new_priority
        task["modified"] = datetime.now().strftime(DATE_FORMAT)
        return self._save_tasks()

# ====================
#    增强型编辑命令
# ====================
@command_handler
def handle_edit(manager, args):
    if len(args) < 1 or not args[0].isdigit():
        raise ValueError("格式: edit <编号> [--priority 级别] [新内容]")
    
    task_id = int(args[0])
    new_priority = None
    content_args = []
    priority_specified = False

    # 灵活解析参数
    i = 1
    while i < len(args):
        if args[i] == "--priority":
            if i+1 >= len(args):
                raise ValueError("需要指定优先级级别")
            new_priority = args[i+1].lower()
            if new_priority not in VALID_PRIORITIES:
                raise ValueError(f"优先级必须是 {', '.join(VALID_PRIORITIES)}")
            i += 2
            priority_specified = True
        else:
            content_args.append(args[i])
            i += 1
    
    new_content = " ".join(content_args) or None  # 允许空内容
    
    if not new_content and not priority_specified:
        raise ValueError("必须提供新内容或修改优先级")
    
    if manager.edit_task(task_id, new_content, new_priority):
        print_color(f"✓ 任务 {task_id} 已修改", "green")

# ====================
#    动态时间对齐显示
# ====================
@command_handler
def handle_list(manager, args):
    # ...（过滤逻辑保持不变）...
    
    # 计算最大列宽
    max_created = max(len(task['created']) for task in filtered) if filtered else 16
    max_modified = max(len(task['modified']) for task in filtered) if filtered else 16
    
    # 表头
    header = color_text(
        f"{'ID':<4} {'状态':<3} {'优先级':<6} {'创建时间':<{max_created}} {'修改时间':<{max_modified}} 内容",
        "yellow"
    )
    print(header)
    
    for task in filtered:
        status_icon = color_text("✓", "green") if task["status"] == "done" else color_text("◻", "red")
        pri_color = PRIORITY_COLORS.get(task["priority"], "yellow")
        pri_mark = color_text("◆", pri_color)
        
        created = color_text(task['created'], "blue").ljust(max_created)
        modified = color_text(task['modified'], "blue").ljust(max_modified)
        
        print(f"#{task['id']:<3} {status_icon} {pri_mark:<2} {created} {modified} {task['content']}")

# ====================
#    完善帮助文档
# ====================
def show_help():
    help_text = """
    命令列表：
      edit <编号> [--priority 级别] [新内容]  
        示例：
        edit 5 --priority high        # 仅修改优先级
        edit 3 "新任务描述"           # 仅修改内容
        edit 7 --priority low 新描述  # 同时修改

      list 支持组合过滤：
        list done priority=high       # 已完成的高优先级任务
        list pending priority=low     # 待处理的低优先级任务

      JSON文件自动备份：
        文件损坏时会自动创建.bak备份
    """
    print(color_text(help_text, "yellow"))

# ...（其他函数保持不变）...

if __name__ == "__main__":
    main()
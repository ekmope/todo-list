
# 文件：retodo_fixed.py
# 命令行Todo List管理系统 - 完整修复版 v3.0

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
MAX_BACKUPS = 5  # 最大保留备份数

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
    return f"{COLOR_MAP.get(color, COLOR_MAP['reset'])}{text}{COLOR_MAP['reset']}" if COLOR_ENABLED else text

def print_color(text, color):
    print(color_text(text, color))

# ====================
#    装饰器：命令处理器
# ====================
def command_handler(func):
    @wraps(func)
    def wrapper(manager, args):
        try:
            func(manager, args)
        except ValueError as e:
            print_color(str(e), "red")
        except Exception as e:
            print_color(f"错误: {e}", "red")
    return wrapper

# ====================
#    Todo 任务管理
# ====================
class TodoManager:
    def __init__(self):
        self.tasks = self._load_tasks()
        self.next_id = self._get_next_id()

    def _load_tasks(self):
        try:
            if not TODO_FILE.exists():
                return []
            backup_time = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_path = TODO_FILE.with_name(f".todo_{backup_time}.bak")
            shutil.copyfile(TODO_FILE, backup_path)
            backup_files = sorted(
                TODO_FILE.parent.glob(".todo_*.bak"),
                key=lambda f: f.name.split("_")[1].split(".")[0],
                reverse=True
            )
            for f in backup_files[MAX_BACKUPS:]:
                try:
                    f.unlink()
                except OSError:
                    pass
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError(f"数据格式错误，已创建备份 {backup_path.name}")
                return data
        except json.JSONDecodeError as e:
            raise ValueError(
                f"数据文件损坏，已创建备份 {backup_path.name}\n错误详情: {str(e)}"
            )
        except Exception as e:
            self._show_error(f"加载失败: {str(e)}")
            try:
                with open(TODO_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return []

    def _get_next_id(self):
        return max((task.get("id", 0) for task in self.tasks), default=0) + 1

    def _find_task(self, task_id):
        return next((task for task in self.tasks if task.get("id") == task_id), None)

    def _save_tasks(self):
        try:
            TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(TODO_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self._show_error(f"保存失败: {e}")
            return False

    def _show_error(self, message):
        print_color(f"错误: {message}", "red")

    def add_task(self, content, priority=None):
        if not content.strip():
            raise ValueError("任务内容不能为空或空白")
        priority = priority or "normal"
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"无效优先级，可选: {', '.join(VALID_PRIORITIES)}")
        task = {
            "id": self.next_id,
            "content": content.strip(),
            "priority": priority,
            "status": "pending",
            "created": datetime.now().strftime(DATE_FORMAT),
            "modified": datetime.now().strftime(DATE_FORMAT)
        }
        self.tasks.append(task)
        if self._save_tasks():
            self.next_id += 1
            return task["id"]
        raise IOError("任务添加失败，无法保存数据")

    def edit_task(self, task_id, new_content=None, new_priority=None):
        task = self._find_task(task_id)
        if not task:
            raise ValueError("找不到指定ID的任务")
        modified = False
        if new_content is not None:
            if not new_content.strip():
                raise ValueError("新内容不能为空或空白")
            task["content"] = new_content.strip()
            modified = True
        if new_priority:
            if new_priority not in VALID_PRIORITIES:
                raise ValueError(f"无效优先级，可选: {', '.join(VALID_PRIORITIES)}")
            task["priority"] = new_priority
            modified = True
        if modified:
            task["modified"] = datetime.now().strftime(DATE_FORMAT)
            return self._save_tasks()
        return False

    def done_task(self, task_id):
        task = self._find_task(task_id)
        if not task:
            raise ValueError("任务ID不存在")
        task["status"] = "done"
        task["modified"] = datetime.now().strftime(DATE_FORMAT)
        return self._save_tasks()

    def remove_task(self, task_id):
        task = self._find_task(task_id)
        if not task:
            raise ValueError("任务ID不存在")
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        return self._save_tasks()

    def clear_tasks(self):
        self.tasks.clear()
        return self._save_tasks()

# ====================
#    命令处理函数
# ====================
@command_handler
def handle_add(manager, args):
    if not args:
        raise ValueError("正确格式: add <内容> [--priority 级别]")
    new_priority = None
    content_parts = []
    i = 0
    while i < len(args):
        if args[i].lower() == "--priority":
            if i + 1 >= len(args):
                raise ValueError("需要指定优先级级别")
            new_priority = args[i + 1].lower()
            i += 2
        else:
            content_parts.append(args[i])
            i += 1
    content = " ".join(content_parts)
    task_id = manager.add_task(content, new_priority)
    print_color(f"✓ 任务 {task_id} 添加成功", "green")

@command_handler
def handle_done(manager, args):
    if len(args) != 1 or not args[0].isdigit():
        raise ValueError("正确格式: done <任务ID>")
    task_id = int(args[0])
    manager.done_task(task_id)
    print_color(f"✓ 任务 {task_id} 已完成", "green")

@command_handler
def handle_remove(manager, args):
    if len(args) != 1 or not args[0].isdigit():
        raise ValueError("正确格式: remove <任务ID>")
    task_id = int(args[0])
    manager.remove_task(task_id)
    print_color(f"✓ 任务 {task_id} 已删除", "green")

@command_handler
def handle_clear(manager, args):
    if args:
        raise ValueError("clear 命令不接受参数")
    manager.clear_tasks()
    print_color("✓ 所有任务已清空", "green")

@command_handler
def handle_edit(manager, args):
    if len(args) < 1 or not args[0].isdigit():
        raise ValueError("正确格式: edit <任务ID> [--priority 级别] [新内容]")
    task_id = int(args[0])
    new_priority = None
    content_parts = []
    i = 1
    while i < len(args):
        if args[i].lower() == "--priority":
            if i + 1 >= len(args):
                raise ValueError("需要指定优先级级别")
            new_priority = args[i + 1].lower()
            i += 2
        else:
            content_parts.append(args[i])
            i += 1
    new_content = " ".join(content_parts) if content_parts else None
    if manager.edit_task(task_id, new_content, new_priority):
        print_color(f"✓ 任务 {task_id} 修改成功", "green")
    else:
        print_color("⚠ 未做任何修改", "yellow")

@command_handler
def handle_list(manager, args):
    tasks = manager.tasks
    for task in tasks:
        status_icon = color_text("✓", "green") if task["status"] == "done" else color_text("◻", "red")
        pri_color = PRIORITY_COLORS.get(task["priority"], "yellow")
        pri_mark = color_text("◆", pri_color)
        print(f"#{task['id']} {status_icon} {pri_mark} {task['created']} -> {task['content']}")

def show_help():
    help_text = """\
命令列表：
  ADD    <内容> [--priority 级别]   添加任务
  EDIT   <ID> [--priority 级别] [内容] 修改任务
  LIST                             显示任务列表
  DONE   <ID>                      标记完成
  REMOVE <ID>                      删除任务
  CLEAR                            清空所有任务
  HELP                             显示帮助
  EXIT                             退出"""
    print(color_text(help_text, "yellow"))

def main():
    manager = TodoManager()
    print_color("\n🚀 Todo管理系统 v3.0", "green")
    print_color("输入 HELP 查看完整命令说明\n", "yellow")
    while True:
        try:
            raw_input_str = input(">> ").strip()
            if not raw_input_str:
                continue
            parts = raw_input_str.split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1].split() if len(parts) > 1 else []
            if cmd == "exit":
                print_color("\n👋 再见！", "green")
                break
            elif cmd == "help":
                show_help()
            elif cmd == "add":
                handle_add(manager, args)
            elif cmd == "done":
                handle_done(manager, args)
            elif cmd == "edit":
                handle_edit(manager, args)
            elif cmd == "list":
                handle_list(manager, args)
            elif cmd == "clear":
                handle_clear(manager, args)
            elif cmd == "remove":
                handle_remove(manager, args)
            else:
                print_color("未知命令，输入 HELP 查看帮助", "red")
        except (KeyboardInterrupt, EOFError):
            print_color("\n👋 再见！", "green")
            break

if __name__ == "__main__":
    main()

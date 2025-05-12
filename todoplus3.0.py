"""
命令行Todo List管理系统 - 增强版
版本：3.0
更新内容：
- 修复参数解析边界问题
- 增强命令容错性
- 优化帮助文档示例
- 完善错误提示信息
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
            # 创建带时间戳的备份
            backup_time = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_path = TODO_FILE.with_name(f".todo_{backup_time}.bak")
            shutil.copyfile(TODO_FILE, backup_path)

            # 清理旧备份
            backup_files = sorted(TODO_FILE.parent.glob(".todo_*.bak"),
                                  key=lambda f: f.stat().st_mtime, reverse=True)
            for f in backup_files[MAX_BACKUPS:]:
                try:
                    f.unlink()
                except OSError:
                    pass

            with open(TODO_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"数据文件损坏，已创建备份 {backup_path.name}\n"
                        f"错误详情: {str(e)}"
                    )
                if not isinstance(data, list):
                    raise ValueError(f"数据格式错误，已创建备份 {backup_path.name}")
                return data
        except Exception as e:
            self._show_error(f"加载失败: {str(e)}")
            # 创建新文件防止后续操作失败
            try:
                with open(TODO_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return []

    def _get_next_id(self):
        if not self.tasks:
            return 1
        try:
            return max(task.get("id", 0) for task in self.tasks) + 1
        except ValueError:
            return 1

    def _find_task(self, task_id):
        for task in self.tasks:
            if task.get("id") == task_id:
                return task
        return None

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
        if not content:
            raise ValueError("任务内容不能为空")
        if priority is None:
            priority = "normal"
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"无效优先级，可选: {', '.join(VALID_PRIORITIES)}")
        task_id = self.next_id
        now = datetime.now().strftime(DATE_FORMAT)
        task = {
            "id": task_id,
            "content": content,
            "priority": priority,
            "status": "pending",
            "created": now,
            "modified": now
        }
        self.tasks.append(task)
        if self._save_tasks():
            self.next_id += 1
            return task_id
        else:
            raise IOError("任务添加失败，无法保存数据")

    def edit_task(self, task_id, new_content=None, new_priority=None):
        task = self._find_task(task_id)
        if not task:
            return False
        # 验证至少有一个修改项
        if new_content is None and new_priority is None:
            self._show_error("必须提供新内容或新优先级")
            return False
        if new_content is not None:
            task["content"] = new_content
        if new_priority:
            if new_priority not in VALID_PRIORITIES:
                self._show_error(f"无效优先级，可选: {', '.join(VALID_PRIORITIES)}")
                return False
            task["priority"] = new_priority
        task["modified"] = datetime.now().strftime(DATE_FORMAT)
        return self._save_tasks()

    def done_task(self, task_id):
        task = self._find_task(task_id)
        if not task:
            return False
        if task.get("status") == "done":
            # 任务已完成，不更新
            return True
        task["status"] = "done"
        task["modified"] = datetime.now().strftime(DATE_FORMAT)
        return self._save_tasks()

    def remove_task(self, task_id):
        for i, task in enumerate(self.tasks):
            if task.get("id") == task_id:
                del self.tasks[i]
                return self._save_tasks()
        return False

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
            if new_priority not in VALID_PRIORITIES:
                raise ValueError(f"优先级必须是 {', '.join(VALID_PRIORITIES)}")
            i += 2
        else:
            content_parts.append(args[i])
            i += 1
    content = " ".join(content_parts).strip()
    if not content:
        raise ValueError("任务内容不能为空")
    task_id = manager.add_task(content, new_priority)
    print_color(f"✓ 任务 {task_id} 添加成功", "green")

@command_handler
def handle_done(manager, args):
    if len(args) < 1 or not args[0].isdigit():
        raise ValueError("正确格式: done <任务ID>")
    task_id = int(args[0])
    if manager.done_task(task_id):
        print_color(f"✓ 任务 {task_id} 已完成", "green")
    else:
        raise ValueError("任务ID不存在")

@command_handler
def handle_list(manager, args):
    # 过滤任务列表
    filtered = manager.tasks.copy()
    for arg in args:
        if "=" in arg:
            key, val = arg.split("=", 1)
            key = key.lower()
            val = val.lower()
            if key == "status":
                if val not in ("done", "pending"):
                    raise ValueError("状态过滤可选值: done, pending")
                filtered = [task for task in filtered if task.get("status") == val]
            elif key == "priority":
                if val not in VALID_PRIORITIES:
                    raise ValueError(f"优先级过滤可选值: {', '.join(VALID_PRIORITIES)}")
                filtered = [task for task in filtered if task.get("priority") == val]
            elif key == "created_after":
                try:
                    date_obj = datetime.strptime(val, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("日期格式应为 YYYY-MM-DD")
                new_filtered = []
                for task in filtered:
                    try:
                        created_dt = datetime.strptime(task.get("created", ""), DATE_FORMAT)
                    except Exception:
                        continue
                    if created_dt >= date_obj:
                        new_filtered.append(task)
                filtered = new_filtered
            else:
                raise ValueError(f"未知过滤条件: {key}")
        else:
            raise ValueError(f"无效参数: {arg}")

    if not filtered:
        print_color("没有符合条件的任务", "yellow")
        return

    # 排序任务，按 ID 升序
    filtered.sort(key=lambda x: x.get("id", 0))

    # 动态计算时间列宽
    max_created = max(len(task.get('created', '')) for task in filtered) if filtered else len("创建时间")
    max_modified = max(len(task.get('modified', '')) for task in filtered) if filtered else len("修改时间")
    max_created = max(max_created, len("创建时间"))
    max_modified = max(max_modified, len("修改时间"))

    # 表头
    header = color_text(
        f"{'ID':<5} {'状态':<4} {'优先级':<7} {'创建时间':<{max_created}} {'修改时间':<{max_modified}} 内容",
        "yellow"
    )
    print(header)
    # 内容行
    for task in filtered:
        status_icon = color_text("✓", "green") if task.get("status") == "done" else color_text("◻", "red")
        pri_color = PRIORITY_COLORS.get(task.get("priority", ""), "yellow")
        pri_mark = color_text("◆", pri_color)
        created = color_text(task.get('created', ''), "blue").ljust(max_created)
        modified = color_text(task.get('modified', ''), "blue").ljust(max_modified)
        print(f"#{task.get('id', ''):<4} {status_icon}  {pri_mark:<2}  {created}  {modified}  {task.get('content', '')}")

@command_handler
def handle_clear(manager, args):
    if args:
        raise ValueError("清空任务不需要额外参数")
    if not manager.tasks:
        print_color("当前没有任务可删除", "yellow")
        return
    manager.clear_tasks()
    print_color("✓ 所有任务已清空", "green")

@command_handler
def handle_remove(manager, args):
    if len(args) < 1 or not args[0].isdigit():
        raise ValueError("正确格式: remove <任务ID>")
    task_id = int(args[0])
    if manager.remove_task(task_id):
        print_color(f"✓ 任务 {task_id} 已删除", "green")
    else:
        raise ValueError("任务ID不存在")

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
            if new_priority not in VALID_PRIORITIES:
                raise ValueError(f"优先级必须是 {', '.join(VALID_PRIORITIES)}")
            i += 2
        else:
            content_parts.append(args[i])
            i += 1

    new_content = " ".join(content_parts) if content_parts else None

    if manager.edit_task(task_id, new_content, new_priority):
        print_color(f"✓ 任务 {task_id} 修改成功", "green")
    else:
        raise ValueError("修改失败，请检查任务ID")

def show_help():
    help_text = """
命令列表（不区分大小写）：
  ADD    <内容> [--priority 级别]   添加任务
  EDIT   <ID> [--priority 级别] [内容] 修改任务
  LIST   [条件]                    显示任务列表
  DONE   <ID>                     标记完成
  REMOVE <ID>                     删除任务
  CLEAR                          清空所有任务
  HELP                           显示帮助
  EXIT                           退出

过滤条件：
  status=[done|pending]          任务状态
  priority=[high|normal|low]     优先级
  created_after=YYYY-MM-DD       创建时间筛选
  示例：
    list status=done priority=high
    list created_after=2023-01-01

数据安全：
  自动保留最近5次备份（.todo_时间戳.bak）
"""
    print(color_text(help_text, "yellow"))

def main():
    manager = TodoManager()
    print(color_text("\n🚀 Todo管理系统 v2.8", "green"))
    print(color_text("输入 HELP 查看完整命令说明\n", "yellow"))

    while True:
        try:
            raw_input = input(">> ").strip()
            if not raw_input:
                continue
            parts = raw_input.split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1].split() if len(parts) > 1 else []
            if cmd == "exit":
                print(color_text("\n👋 再见！", "green"))
                break
            elif cmd == "help":
                show_help()
            elif cmd == "add":
                handle_add(manager, args)
            elif cmd == "done":
                handle_done(manager, args)
            elif cmd == "list":
                handle_list(manager, args)
            elif cmd == "clear":
                handle_clear(manager, args)
            elif cmd == "remove":
                handle_remove(manager, args)
            elif cmd == "edit":
                handle_edit(manager, args)
            else:
                print_color("未知命令，输入 HELP 查看帮助", "red")
        except (EOFError, KeyboardInterrupt):
            print(color_text("\n👋 再见！", "green"))
            break

if __name__ == "__main__":
    main()

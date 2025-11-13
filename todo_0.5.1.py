import os
import sys
import json
from pathlib import Path
from datetime import datetime
from functools import wraps
from shutil import copyfile

# 配置常量（集中管理）
TODO_FILE = Path.home() / ".todo.json"
COLOR_ENABLED = sys.stdout.isatty()
DATE_FORMAT = "%Y-%m-%d %H:%M"
PRI_COLORS = {"high": "red", "normal": "yellow", "low": "blue"}
VALID_PRIS = list(PRI_COLORS.keys())
MAX_BACKUPS = 5
MAX_CONTENT_LEN = 200

# 初始化Windows颜色支持
if COLOR_ENABLED and sys.platform == "win32":
    os.system("color")

COLOR_MAP = {"red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m", "blue": "\033[94m", "reset": "\033[0m"}


# 工具函数（精简合并）
def colorize(text, color):
    return f"{COLOR_MAP.get(color, COLOR_MAP['reset'])}{text}{COLOR_MAP['reset']}" if COLOR_ENABLED else text

def printc(text, color):
    print(colorize(text, color))

def print_task(task):
    status = colorize("✓", "green") if task["status"] == "done" else colorize("◻", "red")
    pri_mark = colorize("◆", PRI_COLORS[task["priority"]])
    modified = f"(修改于: {task['modified']})" if task['modified'] != task['created'] else ""
    print(f"#{task['id']} {status} {pri_mark} {task['created']} {modified} -> {task['content']}")


# 装饰器（保持简洁）
def cmd_handler(func):
    @wraps(func)
    def wrapper(manager, args):
        try:
            func(manager, args)
        except ValueError as e:
            printc(str(e), "red")
        except Exception as e:
            printc(f"错误: {e}", "red")
    return wrapper


class TodoManager:
    def __init__(self):
        self.tasks = self._load()
        self.next_id = max((t["id"] for t in self.tasks), default=0) + 1

    # 加载任务（简化错误处理）
    def _load(self):
        if not TODO_FILE.exists():
            return []
        try:
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("数据格式错误")
                [self._validate(t) for t in data]
                return data
        except (json.JSONDecodeError, ValueError) as e:
            printc(f"数据错误: {e}", "red")
            self._reset_data()
            return []

    # 验证任务格式（简化检查逻辑）
    def _validate(self, task):
        required = ["id", "content", "priority", "status", "created", "modified"]
        if not all(k in task for k in required):
            raise ValueError("缺少必要字段")
        if not isinstance(task["id"], int) or task["id"] <= 0:
            raise ValueError(f"无效ID: {task['id']}")
        if task["priority"] not in VALID_PRIS:
            raise ValueError(f"无效优先级: {task['priority']}")
        if task["status"] not in ["pending", "done"]:
            raise ValueError(f"无效状态: {task['status']}")

    # 重置数据文件
    def _reset_data(self):
        try:
            with open(TODO_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # 查找任务（保持简洁）
    def _find(self, task_id):
        return next((t for t in self.tasks if t["id"] == task_id), None)

    # 保存任务（合并备份逻辑）
    def _save(self):
        try:
            self._backup()
            TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(TODO_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            printc(f"保存失败: {e}", "red")
            return False

    # 备份相关（精简路径处理）
    def _backup(self):
        if not TODO_FILE.exists():
            return
        backup_dir = TODO_FILE.parent / "todo_backups"
        backup_dir.mkdir(exist_ok=True)
        try:
            backup_path = backup_dir / f"todo_{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
            copyfile(TODO_FILE, backup_path)
            # 清理旧备份
            backups = sorted(backup_dir.glob("todo_*.bak"), 
                           key=lambda f: f.stem.split("_")[1], reverse=True)
            for f in backups[MAX_BACKUPS:]:
                f.unlink(missing_ok=True)
        except Exception as e:
            printc(f"备份警告: {e}", "yellow")

    # 核心功能（精简参数检查）
    def add(self, content, priority="normal"):
        content = content.strip()
        if not content or len(content) > MAX_CONTENT_LEN:
            raise ValueError(f"内容不能为空且长度≤{MAX_CONTENT_LEN}")
        if priority not in VALID_PRIS:
            raise ValueError(f"优先级必须是: {', '.join(VALID_PRIS)}")
        
        now = datetime.now().strftime(DATE_FORMAT)
        task = {"id": self.next_id, "content": content, "priority": priority,
                "status": "pending", "created": now, "modified": now}
        self.tasks.append(task)
        if self._save():
            self.next_id += 1
            return task["id"]
        raise IOError("添加失败")

    def edit(self, task_id, new_content=None, new_pri=None):
        self._check_id(task_id)
        task = self._find(task_id) or self._invalid_id(task_id)
        
        modified = False
        if new_content is not None:
            new_content = new_content.strip()
            if not new_content or len(new_content) > MAX_CONTENT_LEN:
                raise ValueError(f"内容不能为空且长度≤{MAX_CONTENT_LEN}")
            task["content"] = new_content
            modified = True
        if new_pri and new_pri in VALID_PRIS:
            task["priority"] = new_pri
            modified = True
        
        if modified:
            task["modified"] = datetime.now().strftime(DATE_FORMAT)
            return self._save()
        return False

    def done(self, task_id):
        self._check_id(task_id)
        task = self._find(task_id) or self._invalid_id(task_id, pending_only=True)
        if task["status"] == "done":
            raise ValueError(f"任务 {task_id} 已完成")
        task["status"] = "done"
        task["modified"] = datetime.now().strftime(DATE_FORMAT)
        return self._save()

    def remove(self, task_id):
        self._check_id(task_id)
        if not self._find(task_id):
            self._invalid_id(task_id)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        return self._save()

    def clear(self):
        if not self.tasks:
            raise ValueError("列表已空")
        self.tasks.clear()
        return self._save()

    def search(self, keyword):
        if not keyword.strip():
            raise ValueError("关键词不能为空")
        return [t for t in self.tasks if keyword.lower() in t["content"].lower()]

    # 提取重复的ID检查逻辑
    def _check_id(self, task_id):
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError(f"ID必须是正整数")

    def _invalid_id(self, task_id, pending_only=False):
        valid_ids = [t["id"] for t in self.tasks if not pending_only or t["status"] == "pending"]
        ids_str = ", ".join(map(str, valid_ids)) if valid_ids else "无可用ID"
        raise ValueError(f"找不到ID {task_id}，可用{'' if not pending_only else '待完成'}ID: {ids_str}")


# 命令处理（简化参数解析）
@cmd_handler
def add_cmd(manager, args):
    if not args:
        raise ValueError("格式: add <内容> [--priority 级别]")
    pri, content_parts = None, []
    i = 0
    while i < len(args):
        if args[i].lower() == "--priority" and i + 1 < len(args):
            pri = args[i+1].lower()
            i += 2
        else:
            content_parts.append(args[i])
            i += 1
    task_id = manager.add(" ".join(content_parts), pri)
    printc(f"✓ 任务 {task_id} 添加成功", "green")

@cmd_handler
def done_cmd(manager, args):
    if len(args) != 1 or not args[0].isdigit():
        raise ValueError("格式: done <任务ID>")
    manager.done(int(args[0]))
    printc(f"✓ 任务 {args[0]} 已完成", "green")

@cmd_handler
def remove_cmd(manager, args):
    if len(args) != 1 or not args[0].isdigit():
        raise ValueError("格式: remove <任务ID>")
    manager.remove(int(args[0]))
    printc(f"✓ 任务 {args[0]} 已删除", "green")

@cmd_handler
def clear_cmd(manager, args):
    if args:
        raise ValueError("clear无参数")
    manager.clear()
    printc("✓ 所有任务已清空", "green")

@cmd_handler
def edit_cmd(manager, args):
    if len(args) < 1 or not args[0].isdigit():
        raise ValueError("格式: edit <ID> [--priority 级别] [新内容]")
    task_id, pri, content_parts = int(args[0]), None, []
    i = 1
    while i < len(args):
        if args[i].lower() == "--priority" and i + 1 < len(args):
            pri = args[i+1].lower()
            i += 2
        else:
            content_parts.append(args[i])
            i += 1
    if manager.edit(task_id, " ".join(content_parts) if content_parts else None, pri):
        printc(f"✓ 任务 {task_id} 修改成功", "green")
    else:
        printc("⚠ 未做任何修改", "yellow")

@cmd_handler
def list_cmd(manager, args):
    if args:
        raise ValueError("list无参数")
    tasks = sorted(manager.tasks, key=lambda t: (t["status"] != "pending", VALID_PRIS.index(t["priority"])))
    if not tasks:
        printc("暂无任务", "yellow")
        return
    [print_task(t) for t in tasks]

@cmd_handler
def search_cmd(manager, args):
    if not args:
        raise ValueError("格式: search <关键词>")
    keyword = " ".join(args)
    results = manager.search(keyword)
    if not results:
        printc(f"无匹配 '{keyword}' 的任务", "yellow")
        return
    printc(f"找到 {len(results)} 个匹配任务:", "green")
    [print_task(t) for t in results]


# 主程序（用字典优化命令分发）
def main():
    manager = TodoManager()
    printc("\n🚀 Todo管理系统 v5.0", "green")
    printc("输入 HELP 查看命令说明\n", "yellow")
    
    cmd_map = {
        "add": add_cmd, "done": done_cmd, "edit": edit_cmd,
        "list": list_cmd, "search": search_cmd, "clear": clear_cmd,
        "remove": remove_cmd
    }

    while True:
        try:
            inp = input(">> ").strip()
            if not inp:
                continue
            cmd, *args = inp.split()
            cmd = cmd.lower()
            if cmd == "exit":
                printc("\n👋 再见！", "green")
                break
            elif cmd == "help":
                printc("""
命令列表：
  ADD    <内容> [--priority 级别]   添加任务 (级别: high/normal/low)
  EDIT   <ID> [--priority 级别] [内容] 修改任务
  LIST                             显示所有任务
  SEARCH <关键词>                  搜索任务
  DONE   <ID>                      标记完成
  REMOVE <ID>                      删除任务
  CLEAR                            清空所有
  HELP                             帮助
  EXIT                             退出""", "yellow")
            elif cmd in cmd_map:
                cmd_map[cmd](manager, args)
            else:
                printc("未知命令，输入HELP查看帮助", "red")
        except (KeyboardInterrupt, EOFError):
            printc("\n👋 再见！", "green")
            break


if __name__ == "__main__":
    main()
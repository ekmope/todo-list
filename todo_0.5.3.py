import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
from shutil import copyfile

# 配置常量（新增截止日期格式说明）
TODO_FILE = Path.home() / ".todo.json"
COLOR_ENABLED = sys.stdout.isatty()
DATE_FORMAT = "%Y-%m-%d %H:%M"  # 统一用于创建/修改时间和截止日期
PRI_COLORS = {"high": "red", "normal": "yellow", "low": "blue"}
VALID_PRIS = list(PRI_COLORS.keys())
MAX_BACKUPS = 5
MAX_CONTENT_LEN = 200

# 初始化Windows颜色支持
if COLOR_ENABLED and sys.platform == "win32":
    os.system("color")

COLOR_MAP = {"red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m", "blue": "\033[94m", "reset": "\033[0m"}


# 工具函数（新增截止日期格式化和过期检查）
def colorize(text, color):
    return f"{COLOR_MAP.get(color, COLOR_MAP['reset'])}{text}{COLOR_MAP['reset']}" if COLOR_ENABLED else text

def printc(text, color):
    print(colorize(text, color))

def parse_due_date(date_str):
    """支持多种日期格式的解析函数"""
    if not date_str or date_str.lower() == "none":
        return None
    
    # 支持的日期格式列表
    formats = [
        "%Y-%m-%d %H:%M",  # 完整格式
        "%Y-%m-%d",        # 仅日期
        "%m/%d",           # 月/日（当年）
        "%m-%d",           # 月-日（当年）
        "%Y/%m/%d",        # 年/月/日
        "%Y%m%d"           # 紧凑格式
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # 如果只有日期，默认设置为23:59截止
            if fmt in ["%Y-%m-%d", "%m/%d", "%m-%d", "%Y/%m/%d", "%Y%m%d"]:
                dt = dt.replace(hour=23, minute=59)
                # 对于没有年份的格式，使用当前年份
                if fmt in ["%m/%d", "%m-%d"]:
                    dt = dt.replace(year=datetime.now().year)
            return dt.strftime(DATE_FORMAT)
        except ValueError:
            continue
    
    # 尝试相对时间（如"tomorrow", "3days"）
    date_str_lower = date_str.lower()
    if date_str_lower == "tomorrow":
        return (datetime.now() + timedelta(days=1)).replace(hour=23, minute=59).strftime(DATE_FORMAT)
    elif date_str_lower == "today":
        return datetime.now().replace(hour=23, minute=59).strftime(DATE_FORMAT)
    elif date_str_lower.endswith("days"):
        try:
            days = int(date_str_lower[:-4])
            return (datetime.now() + timedelta(days=days)).replace(hour=23, minute=59).strftime(DATE_FORMAT)
        except ValueError:
            pass
    
    raise ValueError(f"日期格式错误，支持格式: 完整({DATE_FORMAT})、日期(YYYY-MM-DD)、相对时间(today/tomorrow/3days)等")

def is_overdue(due_date):
    """检查任务是否已过期"""
    if not due_date:
        return False
    try:
        due = datetime.strptime(due_date, DATE_FORMAT)
        return datetime.now() > due
    except:
        return False

def print_task(task):
    status = colorize("✓", "green") if task["status"] == "done" else colorize("◻", "red")
    pri_mark = colorize("◆", PRI_COLORS[task["priority"]])
    modified = f"(修改于: {task['modified']})" if task['modified'] != task['created'] else ""
    
    # 处理截止日期显示（过期标红）
    due_str = ""
    if task.get("due_date"):
        due_color = "red" if is_overdue(task["due_date"]) else "blue"
        due_str = colorize(f"[截止: {task['due_date']}]", due_color)
    
    print(f"#{task['id']} {status} {pri_mark} {task['created']} {modified} {due_str} -> {task['content']}")


# 装饰器（保持不变）
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

    # 加载任务（更新验证逻辑以支持due_date）
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

    # 验证任务格式（新增due_date字段检查和数据兼容性）
    def _validate(self, task):
        required = ["id", "content", "priority", "status", "created", "modified"]
        if not all(k in task for k in required):
            raise ValueError("缺少必要字段")
        
        # 数据兼容性：自动补全旧版本数据
        if "due_date" not in task:
            task["due_date"] = None
        
        # 可选字段due_date格式验证
        if task["due_date"]:
            try:
                datetime.strptime(task["due_date"], DATE_FORMAT)
            except ValueError:
                raise ValueError(f"截止日期格式错误: {task['due_date']}（应为{DATE_FORMAT}）")
        
        if not isinstance(task["id"], int) or task["id"] <= 0:
            raise ValueError(f"无效ID: {task['id']}")
        if task["priority"] not in VALID_PRIS:
            raise ValueError(f"无效优先级: {task['priority']}")
        if task["status"] not in ["pending", "done"]:
            raise ValueError(f"无效状态: {task['status']}")

    # 重置数据文件（保持不变）
    def _reset_data(self):
        try:
            with open(TODO_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # 查找任务（保持不变）
    def _find(self, task_id):
        return next((t for t in self.tasks if t["id"] == task_id), None)

    # 保存任务（保持不变）
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

    # 备份相关（保持不变）
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

    # 核心功能（新增截止日期支持）
    def add(self, content, priority="normal", due_date=None):
        content = content.strip()
        if not content or len(content) > MAX_CONTENT_LEN:
            raise ValueError(f"内容不能为空且长度≤{MAX_CONTENT_LEN}")
        if priority not in VALID_PRIS:
            raise ValueError(f"优先级必须是: {', '.join(VALID_PRIS)}")
        
        # 使用新的日期解析函数
        parsed_due = parse_due_date(due_date) if due_date else None
        
        now = datetime.now().strftime(DATE_FORMAT)
        task = {
            "id": self.next_id, 
            "content": content, 
            "priority": priority,
            "status": "pending", 
            "created": now, 
            "modified": now,
            "due_date": parsed_due
        }
        self.tasks.append(task)
        if self._save():
            self.next_id += 1
            return task["id"]
        raise IOError("添加失败")

    def edit(self, task_id, new_content=None, new_pri=None, new_due=None):
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
        # 处理截止日期编辑（使用新的解析函数）
        if new_due is not None:
            task["due_date"] = parse_due_date(new_due)
            modified = True
        
        if modified:
            task["modified"] = datetime.now().strftime(DATE_FORMAT)
            return self._save()
        return False

    # 新增：数据统计功能（扩展时间维度）
    def get_stats(self):
        total = len(self.tasks)
        if total == 0:
            return {"total": 0}
        done = sum(1 for t in self.tasks if t["status"] == "done")
        pending = total - done
        # 优先级分布
        pri_counts = {pri: sum(1 for t in self.tasks if t["priority"] == pri) for pri in VALID_PRIS}
        # 过期任务数
        overdue = sum(1 for t in self.tasks if t["status"] == "pending" and is_overdue(t.get("due_date")))
        
        # 新增时间维度统计
        today = datetime.now().strftime("%Y-%m-%d")
        created_today = sum(1 for t in self.tasks if t["created"].startswith(today))
        completed_today = sum(1 for t in self.tasks if t["status"] == "done" and t["modified"].startswith(today))
        
        # 本周统计
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        created_this_week = sum(1 for t in self.tasks if t["created"] >= week_ago)
        completed_this_week = sum(1 for t in self.tasks if t["status"] == "done" and t["modified"] >= week_ago)
        
        return {
            "total": total,
            "done": done,
            "pending": pending,
            "priority": pri_counts,
            "overdue": overdue,
            "created_today": created_today,
            "completed_today": completed_today,
            "created_this_week": created_this_week,
            "completed_this_week": completed_this_week
        }

    # 以下方法保持原有逻辑，仅适配截止日期字段
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

    def _check_id(self, task_id):
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError(f"ID必须是正整数")

    def _invalid_id(self, task_id, pending_only=False):
        valid_ids = [t["id"] for t in self.tasks if not pending_only or t["status"] == "pending"]
        ids_str = ", ".join(map(str, valid_ids)) if valid_ids else "无可用ID"
        raise ValueError(f"找不到ID {task_id}，可用{'' if not pending_only else '待完成'}ID: {ids_str}")


# 命令处理（使用argparse改进参数解析）
def create_add_parser():
    parser = argparse.ArgumentParser(prog="add")
    parser.add_argument("content", help="任务内容")
    parser.add_argument("--priority", choices=VALID_PRIS, default="normal", help="优先级")
    parser.add_argument("--due", help="截止日期（支持多种格式：YYYY-MM-DD HH:MM、YYYY-MM-DD、today、tomorrow、3days等）")
    return parser

def create_edit_parser():
    parser = argparse.ArgumentParser(prog="edit")
    parser.add_argument("task_id", type=int, help="任务ID")
    parser.add_argument("--priority", choices=VALID_PRIS, help="优先级")
    parser.add_argument("--due", help="截止日期（输入'none'清除，支持多种格式）")
    parser.add_argument("content", nargs="?", help="新内容")
    return parser

def create_list_parser():
    parser = argparse.ArgumentParser(prog="list")
    parser.add_argument("--due", action="store_true", help="按截止日期排序")
    return parser

@cmd_handler
def add_cmd(manager, args):
    parser = create_add_parser()
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        raise ValueError(f"格式: add <内容> [--priority 级别] [--due 日期]")
    
    task_id = manager.add(parsed_args.content, parsed_args.priority, parsed_args.due)
    printc(f"✓ 任务 {task_id} 添加成功", "green")

@cmd_handler
def done_cmd(manager, args):
    parser = argparse.ArgumentParser(prog="done")
    parser.add_argument("task_id", type=int, help="任务ID")
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        raise ValueError("格式: done <任务ID>")
    
    manager.done(parsed_args.task_id)
    printc(f"✓ 任务 {parsed_args.task_id} 已完成", "green")

@cmd_handler
def remove_cmd(manager, args):
    parser = argparse.ArgumentParser(prog="remove")
    parser.add_argument("task_id", type=int, help="任务ID")
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        raise ValueError("格式: remove <任务ID>")
    
    manager.remove(parsed_args.task_id)
    printc(f"✓ 任务 {parsed_args.task_id} 已删除", "green")

@cmd_handler
def clear_cmd(manager, args):
    if args:
        raise ValueError("clear无参数")
    manager.clear()
    printc("✓ 所有任务已清空", "green")

@cmd_handler
def edit_cmd(manager, args):
    parser = create_edit_parser()
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        raise ValueError(f"格式: edit <ID> [--priority 级别] [--due 日期|none] [新内容]")
    
    if manager.edit(parsed_args.task_id, parsed_args.content, parsed_args.priority, parsed_args.due):
        printc(f"✓ 任务 {parsed_args.task_id} 修改成功", "green")
    else:
        printc("⚠ 未做任何修改", "yellow")

@cmd_handler
def list_cmd(manager, args):
    parser = create_list_parser()
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        raise ValueError("list可选参数: --due（按截止日期排序）")
    
    if parsed_args.due:
        # 按截止日期排序（无截止日期的放最后）
        tasks = sorted(
            manager.tasks,
            key=lambda t: (
                t["status"] != "pending",  # 待办在前
                t.get("due_date") is None,  # 有截止日期的在前
                t.get("due_date") or "9999-12-31 23:59"  # 按日期升序
            )
        )
    else:
        # 原有排序逻辑（待办在前，按优先级）
        tasks = sorted(
            manager.tasks,
            key=lambda t: (t["status"] != "pending", VALID_PRIS.index(t["priority"]))
        )
    
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

# 新增：统计命令
@cmd_handler
def stats_cmd(manager, args):
    if args:
        raise ValueError("stats无参数")
    stats = manager.get_stats()
    if stats["total"] == 0:
        printc("暂无任务数据", "yellow")
        return
    
    printc("\n📊 任务统计:", "green")
    print(f"总任务数: {stats['total']}")
    print(f"已完成: {stats['done']} ({stats['done']/stats['total']*100:.1f}%)")
    print(f"待完成: {stats['pending']}")
    print(f"已过期: {colorize(stats['overdue'], 'red')}")  # 过期标红
    
    # 新增时间维度统计
    print(f"\n📅 时间统计:")
    print(f"今日新增: {stats['created_today']}")
    print(f"今日完成: {stats['completed_today']}")
    print(f"本周新增: {stats['created_this_week']}")
    print(f"本周完成: {stats['completed_this_week']}")
    
    print("\n优先级分布:")
    for pri in VALID_PRIS:
        print(f"  {pri}: {stats['priority'][pri]}")
    print()


# 主程序（支持命令缩写和过期提醒）
def main():
    manager = TodoManager()
    printc("\n🚀 Todo管理系统 v5.3", "green")
    printc("输入 HELP 查看命令说明\n", "yellow")
    
    # 新增：启动时检查过期任务提醒
    overdue_count = sum(1 for t in manager.tasks if t["status"] == "pending" and is_overdue(t.get("due_date")))
    if overdue_count > 0:
        printc(f"⚠️ 您有 {overdue_count} 个任务已过期！使用 'list --due' 查看", "red")
        print()
    
    # 命令映射（支持缩写：如a→add，l→list）
    cmd_map = {
        "add": add_cmd, "a": add_cmd,
        "done": done_cmd, "d": done_cmd,
        "edit": edit_cmd, "e": edit_cmd,
        "list": list_cmd, "l": list_cmd,
        "search": search_cmd, "s": search_cmd,
        "clear": clear_cmd, "c": clear_cmd,
        "remove": remove_cmd, "r": remove_cmd,
        "stats": stats_cmd, "st": stats_cmd
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
            elif cmd == "help" or cmd == "h":  # 帮助命令缩写
                printc(f"""
命令列表（支持缩写）：
  ADD(a)   <内容> [--priority 级别] [--due 日期]  添加任务
           日期格式: YYYY-MM-DD HH:MM、YYYY-MM-DD、today、tomorrow、3days等
  EDIT(e)  <ID> [--priority 级别] [--due 日期|none] [内容]  修改任务
  LIST(l)  [--due]                  显示所有任务（--due按截止日期排序）
  SEARCH(s) <关键词>                搜索任务
  DONE(d)  <ID>                     标记完成
  REMOVE(r) <ID>                    删除任务
  CLEAR(c)                          清空所有
  STATS(st)                         查看统计数据（含时间维度）
  HELP(h)                           帮助
  EXIT                              退出""", "yellow")
            elif cmd in cmd_map:
                cmd_map[cmd](manager, args)
            else:
                printc("未知命令，输入HELP查看帮助", "red")
        except (KeyboardInterrupt, EOFError):
            printc("\n👋 再见！", "green")
            break


if __name__ == "__main__":
    main()

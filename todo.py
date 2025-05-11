import os
import sys
from functools import wraps

# ====================
#    配置项
# ====================
TODO_FILE = os.path.join(os.path.expanduser("~"), ".todo.txt")  # 用户主目录存储
COLOR_ENABLED = True  # 是否启用颜色输出

# ====================
#    颜色支持
# ====================
if COLOR_ENABLED and sys.platform == "win32":
    os.system("color")  # Windows启用ANSI转义

COLOR = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "reset": "\033[0m"
}

def color_text(text, color):
    return f"{COLOR[color]}{text}{COLOR['reset']}" if COLOR_ENABLED else text

# ====================
#    核心逻辑
# ====================
class TodoManager:
    def __init__(self):
        self.tasks = self._load_tasks()

    def _load_tasks(self):
        """加载任务文件"""
        try:
            if os.path.exists(TODO_FILE):
                with open(TODO_FILE, "r") as f:
                    return [line.strip() for line in f]
            return []
        except IOError as e:
            print(color_text(f"错误：无法读取任务文件 ({e})", "red"))
            return []

    def _save_tasks(self):
        """保存任务文件（带错误处理）"""
        try:
            with open(TODO_FILE, "w") as f:
                f.write("\n".join(self.tasks))
            return True
        except IOError as e:
            print(color_text(f"错误：无法保存任务文件 ({e})", "red"))
            return False

    def add_task(self, content):
        """添加新任务"""
        self.tasks.append(f"[ ] {content}")
        return self._save_tasks()

    def complete_task(self, task_id):
        """标记任务完成"""
        if 1 <= task_id <= len(self.tasks):
            self.tasks[task_id-1] = self.tasks[task_id-1].replace("[ ]", "[x]")
            return self._save_tasks()
        return False

    def clear_tasks(self):
        """清空所有任务"""
        self.tasks = []
        return self._save_tasks()

# ====================
#    命令处理
# ====================
def command_handler(func):
    """统一错误处理装饰器"""
    @wraps(func)
    def wrapper(manager, *args):
        try:
            return func(manager, *args)
        except Exception as e:
            print(color_text(f"错误：{e}", "red"))
    return wrapper

@command_handler
def handle_add(manager, args):
    if not args:
        raise ValueError("任务内容不能为空")
    manager.add_task(" ".join(args))
    print(color_text(f"✓ 已添加任务: {args[0]}", "green"))

@command_handler
def handle_done(manager, args):
    if not args or not args[0].isdigit():
        raise ValueError("需要有效的任务编号")
    
    task_id = int(args[0])
    if manager.complete_task(task_id):
        print(color_text(f"✓ 任务 {task_id} 已完成！", "green"))
    else:
        raise ValueError("无效的任务编号")

@command_handler
def handle_list(manager, _):
    if not manager.tasks:
        print(color_text("当前没有任务", "yellow"))
        return
    
    for i, task in enumerate(manager.tasks, 1):
        status = color_text("✓", "green") if "[x]" in task else color_text("◻", "red")
        print(f"{i:2}. {status} {task[4:]}")

@command_handler
def handle_clear(manager, _):
    confirm = input(color_text("确认清空所有任务？(y/N): ", "red"))
    if confirm.lower() == "y":
        manager.clear_tasks()
        print(color_text("✓ 所有任务已清空", "green"))

# ====================
#    主程序
# ====================
def show_help():
    help_text = """
    命令列表：
      add <内容>    添加新任务
      done <编号>   标记任务完成
      list         显示任务列表
      clear        清空所有任务
      help         显示帮助信息
      exit         退出程序
    """
    print(color_text(help_text, "yellow"))

def main():
    manager = TodoManager()
    print(color_text("\n🚀 欢迎使用Todo List管理系统", "green"))
    print(color_text("输入 'help' 查看可用命令\n", "yellow"))

    while True:
        try:
            cmd, *args = input(">> ").strip().split(maxsplit=1)
            args = args[0].split() if args else []
        except ValueError:
            continue

        cmd = cmd.lower()
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
        else:
            print(color_text("未知命令，输入 'help' 查看帮助", "red"))

if __name__ == "__main__":
    main()
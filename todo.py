import os
import sys

TODO_FILE = "todo.txt"

def load_tasks():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            return f.read().splitlines()
    return []

def save_tasks(tasks):
    with open(TODO_FILE, 'w') as f:
        f.write('\n'.join(tasks))

def show_help():
    print("""命令列表：
    add <任务内容>   添加任务
    done <任务编号>  标记任务完成
    list            显示所有任务
    clear           清空所有任务
    help            显示帮助
    exit            退出程序""")

def main():
    tasks = load_tasks()
    print("欢迎使用命令行待办清单！输入 'help' 查看命令")
    
    while True:
        command = input("\n请输入命令: ").strip().split()
        if not command:
            continue
        
        action = command[0].lower()
        
        if action == 'add' and len(command) > 1:
            task = ' '.join(command[1:])
            tasks.append(f"[ ] {task}")
            save_tasks(tasks)
            print(f"已添加任务: {task}")
            
        elif action == 'done' and len(command) > 1:
            try:
                index = int(command[1]) - 1
                if 0 <= index < len(tasks):
                    tasks[index] = tasks[index].replace("[ ]", "[x]")
                    save_tasks(tasks)
                    print(f"任务 {index+1} 已完成！")
                else:
                    print("无效的任务编号")
            except ValueError:
                print("请输入正确的任务编号（数字）")
                
        elif action == 'list':
            if not tasks:
                print("当前没有任务~")
            else:
                for i, task in enumerate(tasks, 1):
                    print(f"{i}. {task}")
                    
        elif action == 'clear':
            tasks = []
            save_tasks(tasks)
            print("所有任务已清空")
            
        elif action == 'help':
            show_help()
            
        elif action == 'exit':
            print("再见！")
            break
            
        else:
            print("未知命令，输入 'help' 查看帮助")

if __name__ == "__main__":
    main()
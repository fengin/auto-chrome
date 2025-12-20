# https://aibook.ren (AI全书)
import argparse
import sys
import importlib
from framework.core.context import Context

def main():
    parser = argparse.ArgumentParser(description="Auto-Chrome Browser Automation Framework")
    parser.add_argument("--task", type=str, required=True, help="Task module path (e.g., tasks.examples.linux_do_browser.LinuxDoBrowserTask)")
    parser.add_argument("--config", type=str, default="config/settings.yaml", help="Path to configuration file")
    
    args = parser.parse_args()

    # Initialize Context
    # 初始化上下文
    try:
        context = Context(args.config)
    except Exception as e:
        print(f"Failed to initialize context: {e}")
        sys.exit(1)

    logger = context.get_logger("Main")
    
    # Discover and Resolve Task
    # 发现并解析任务
    from framework.core.registry import discover_tasks
    available_tasks = discover_tasks()
    
    task_input = args.task
    TaskClass = None
    
    # Check if input matches a discovered task name
    # 检查输入是否匹配已发现的任务名称
    if task_input in available_tasks:
        TaskClass = available_tasks[task_input]
        logger.info(f"Found task '{task_input}' in registry.")
    else:
        # Fallback: Try manual import format 'module.path.ClassName'
        # 回退：尝试手动导入格式 'module.path.ClassName'
        try:
            if "." in task_input:
                module_path, class_name = task_input.rsplit(".", 1)
                module = importlib.import_module(module_path)
                TaskClass = getattr(module, class_name)
        except (ImportError, AttributeError, ValueError) as e:
            logger.debug(f"Direct import failed: {e}")

    if not TaskClass:
        logger.error(f"Task '{task_input}' not found!")
        logger.info("Available tasks:")
        for name in available_tasks.keys():
            logger.info(f" - {name}")
        sys.exit(1)

    # Execute Task
    try:
        task_instance = TaskClass(context)
        task_instance.execute()
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

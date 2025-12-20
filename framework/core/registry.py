# https://aibook.ren (AI全书)
import os
import pkgutil
import importlib
import inspect
from typing import Dict, Type
from framework.core.task_base import BaseTask
from framework.utils.logger import setup_logger

logger = setup_logger("TaskRegistry")

def discover_tasks(package_path: str = "tasks") -> Dict[str, Type[BaseTask]]:
    """
    Scans the given package path for classes inheriting from BaseTask.
    Returns a dictionary mapping task names to task classes.
    扫描给定的包路径，查找继承自 BaseTask 的类。
    返回一个将任务名称映射到任务类的字典。
    """
    found_tasks = {}
    
    # Ensure standard execution path
    # 确保标准的执行路径
    root_dir = os.getcwd()
    tasks_dir = os.path.join(root_dir, package_path)
    
    if not os.path.exists(tasks_dir):
        logger.warning(f"Tasks directory not found: {tasks_dir}")
        return found_tasks

    # Recursively find modules
    # 递归查找模块
    for root, dirs, files in os.walk(tasks_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                # Convert file path to module path
                # 将文件路径转换为模块路径
                rel_path = os.path.relpath(os.path.join(root, file), root_dir)
                module_name = rel_path.replace(os.sep, ".").replace(".py", "")
                
                try:
                    module = importlib.import_module(module_name)
                    
                    # Inspect module for Task classes
                    # 检查模块中的 Task 类
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseTask) and 
                            obj is not BaseTask):
                            
                            task_name = getattr(obj, "name", None)
                            if not task_name:
                                # Fallback to class name if no name property is set
                                # 如果未设置 name 属性，则回退到类名
                                task_name = name
                            
                            found_tasks[task_name] = obj
                            # logger.debug(f"Discovered task: {task_name} -> {module_name}.{name}")
                            
                except Exception as e:
                    logger.error(f"Failed to load module {module_name}: {e}")

    return found_tasks

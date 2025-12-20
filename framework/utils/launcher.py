# https://aibook.ren (AI全书)
import subprocess
import os
import sys
from framework.core.context import Context

def launch_chrome(config_path: str = "config/settings.yaml"):
    """
    Launches Chrome based on the provided configuration.
    根据提供的配置启动 Chrome。
    """
    
    try:
        context = Context(config_path)
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    logger = context.get_logger("Launcher")
    chrome_config = context.config.chrome

    executable_path = chrome_config.get("executable_path")
    user_data_dir = chrome_config.get("user_data_dir")
    debug_port = chrome_config.get("debug_port")
    launch_args = chrome_config.get("launch_args", [])

    if not executable_path or not os.path.exists(executable_path):
        logger.error(f"Chrome executable not found at: {executable_path}")
        return

    # Basic arguments / 基本参数
    cmd = [executable_path]
    
    # Add configured arguments (ensure no duplicates)
    # 添加配置的参数（确保无重复）
    final_args = set(launch_args)
    final_args.add(f"--remote-debugging-port={debug_port}")
    final_args.add(f"--user-data-dir={user_data_dir}")
    
    # Convert back to list for subprocess
    # 转回列表供 subprocess 使用
    cmd.extend(list(final_args))

    logger.info(f"Launching Chrome...")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        # Popen is used to launch without blocking the script completely (though it's a detached process essentially)
        # Using start command on Windows to ensure it opens in a new window/process group
        # Popen 用于启动而不完全阻塞脚本（虽然本质上是一个分离的进程）
        # 在 Windows 上使用 start 命令以确保它在一个新的窗口/进程组中打开
        if sys.platform == "win32":
             subprocess.Popen(cmd, shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
             subprocess.Popen(cmd)
             
        logger.info("Chrome launched successfully.")
        logger.info(f"Debug Port: {debug_port}")
        logger.info(f"User Data Dir: {user_data_dir}")
        
    except Exception as e:
        logger.error(f"Failed to launch Chrome: {e}")

if __name__ == "__main__":
    launch_chrome()

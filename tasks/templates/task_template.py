# https://aibook.ren (AI全书)
from framework.core.task_base import BaseTask

class BasicTaskTemplate(BaseTask):
    """
    A basic template for creating new browser automation tasks.
    创建新的浏览器自动化任务的基础模板。
    
    Instruction / 使用说明:
    1. Copy this file to `tasks/your_task_name.py`
       复制此文件到 `tasks/your_task_name.py`
    2. Rename the class to something descriptive (e.g., `MyShoppingTask`)
       将类重命名为描述性名称（例如 `MyShoppingTask`）
    3. Update the `name` attribute below.
       更新下方的 `name` 属性。
    4. Implement your logic in the `run` method.
       在 `run` 方法中实现你的逻辑。
    """
    
    # [REQUIRED] Unique name for running via: python main.py --task my_task_name
    # [必须] 唯一名称，用于通过命令运行: python main.py --task my_task_name
    name = "basic_template" 

    def run(self):
        """
        The main execution entry point.
        The driver is already initialized and available at self.driver.
        执行入口点。驱动程序已初始化并通过 self.driver 可用。
        """
        
        # 1. Get the page object
        # 1. 获取页面对象
        page = self.driver.get_page()
        
        # 2. Add your logic here
        # 2. 在此处添加逻辑
        self.logger.info("Starting Basic Task...")
        
        target_url = "https://example.com"
        self.logger.info(f"Navigating to {target_url}")
        page.goto(target_url)
        
        # 3. Example Interaction
        # 3. 交互示例
        # page.click("#some-button")
        # page.type("#search", "hello world")

        # 4. [Optional] AI Integration Example
        # 4. [可选] AI 集成示例
        # from framework.ai.agent import MockAgent
        # agent = MockAgent()
        # content = page.content()
        # summary = agent.analyze_page(content[:1000])
        # self.logger.info(f"AI Analysis: {summary}")
        
        self.logger.info("Task completed successfully.")

# https://aibook.ren (AI全书)
from abc import ABC, abstractmethod
from framework.core.context import Context
from framework.core.driver import BrowserDriver

class BaseTask(ABC):
    name: str = "" # Unique identifier for the task / 任务的唯一标识符

    def __init__(self, context: Context):
        self.context = context
        self.logger = context.get_logger(self.__class__.__name__)
        self.driver = BrowserDriver(context)

    @abstractmethod
    def run(self):
        """
        Main execution logic for the task.
        任务的主要执行逻辑。
        """
        pass

    def setup(self):
        """
        Prepare environment, connect driver.
        准备环境，连接驱动。
        """
        self.logger.info("Setting up task...")
        self.driver.start()

    def teardown(self):
        """
        Clean up resources.
        清理资源。
        """
        self.logger.info("Tearing down task...")
        self.driver.close()

    def execute(self):
        """
        Template method to execute the task securely.
        安全执行任务的模板方法。
        """
        try:
            self.setup()
            self.run()
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}", exc_info=True)
            raise
        finally:
            self.teardown()

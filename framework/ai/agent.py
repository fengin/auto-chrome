# https://aibook.ren (AI全书)
from abc import ABC, abstractmethod
from typing import Any, Dict

class AIAgent(ABC):
    @abstractmethod
    def analyze_page(self, content: str) -> str:
        """
        Analyzes the page content and returns a summary or insight.
        分析页面内容并返回摘要或见解。
        """
        pass

    @abstractmethod
    def extract_structure(self, content: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts structured data from the content based on a schema.
        基于模式从内容中提取结构化数据。
        """
        pass

class MockAgent(AIAgent):
    """
    A mock agent for testing without LLM costs.
    用于测试的模拟代理，不产生 LLM 成本。
    """
    def analyze_page(self, content: str) -> str:
        return f"Mock analysis of {len(content)} chars."

    def extract_structure(self, content: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        return {"mock_key": "mock_value"}

# Auto-Chrome

**Auto-Chrome** is a powerful automation framework designed to boost daily productivity. It enables you to easily automate **web browsing tasks**, **data collection & organization**, **information retrieval & report writing**, **automated testing**, and various **web-based office automation** scenarios.

By taking over existing browser sessions via **CDP (Chrome DevTools Protocol)** and leveraging the power of **Playwright**, along with built-in **AI Agent** interfaces, it makes writing complex "Human-in-the-loop" or "AI-driven" automation tasks effortless.

## ✨ Features

*   **⚡ Efficient Office Work**: Automate repetitive web operations to free up manpower.
*   **📊 Data Insights**: Easily collect, clean, and organize web data to assist decision-making.
*   **🧩 Modular Design**: Decoupled core driver, task logic, and configuration management.
*   **🤖 AI Ready**: Built-in `AIAgent` interface for seamless integration with LLMs for intelligent analysis and report generation.
*   **🔌 Auto Discovery**: Plug-and-play task scripts. The framework automatically scans and registers tasks.
*   **🐍 Python First**: Pure Python implementation, easy to extend and maintain.
*   **📝 Bilingual Comments**: Core code contains full Chinese/English bilingual comments for easier source reading.

## 👤 Author Info

*   **Author**: Ling Feng (凌封)
*   **Website**: [AI Book (AI全书)](https://aibook.ren)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install playwright pyyaml
playwright install
```

### 2. Launch Browser
Use the built-in script to launch Chrome with remote debugging enabled:
```bash
python launch_browser.py
```
*(Note: Please log in to your target websites in the popped-up browser window)*

### 3. Run Example Task
Runs the included Linux.do forum browsing example:
```bash
python main.py --task linux_do
```

### 4. Configuration (Optional)
The framework reads `config/settings.yaml`. You can modify it to fit your environment (e.g., Chrome path, debug port):
```yaml
chrome:
  executable_path: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
  debug_port: 9222
```

## 🛠️ Development Guide

### Create a New Task
Create a new file in the `tasks/` directory, e.g., `my_task.py`, and inherit from `BaseTask`:

```python
from framework.core.task_base import BaseTask

class MyTask(BaseTask):
    name = "my_task" # Implementation name for CLI

    def run(self):
        page = self.driver.get_page()
        page.goto("https://www.google.com")
        self.logger.info("Opened Google")
```

Then run it directly:
```bash
python main.py --task my_task
```

**Tip:** `tasks/templates/task_template.py` contains a detailed template with comments and AI examples. It's recommended to copy this file to start development.

## 📂 Project Structure

```text
auto-chrome/
├── framework/          # Core framework code
│   ├── core/           # Driver, BaseTask, Context
│   ├── ai/             # AI Agent Interface
│   └── utils/          # Utilities
├── tasks/              # Task scripts
│   ├── examples/       # Example tasks
│   └── templates/      # Task templates
├── config/             # Configuration files
├── launch_browser.py   # Browser launcher
└── main.py             # Main entry point
```

## 🤝 Contribution
Issues and Pull Requests are welcome!

## 📄 License
MIT License

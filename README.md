# Auto-Chrome

**Auto-Chrome** 是一个功能强大的自动化框架，专为提升日常工作效率而设计。基于该框架，你可以轻松实现**网页浏览任务自动化**、**数据采集与整理**、**信息检索与研报编写**、**自动化测试**以及各类**自动化网页办公**场景。

它通过 **CDP (Chrome DevTools Protocol)** 接管现有的浏览器会话，结合 **Playwright** 的强大控制力，并内置了 **AI Agent** 接口，使编写复杂的“人机协同”或“AI 驱动”的任务变得简单。

## ✨ 特性

*   **⚡ 高效办公**: 自动化处理重复性网页操作，释放人力。
*   **📊 数据洞察**: 轻松采集、清洗和整理网页数据，辅助决策。
*   **🧩 模块化设计**: 核心驱动、任务逻辑、配置管理完全解耦。
*   **🤖 AI Ready**: 内置 `AIAgent` 接口，支持打通 LLM 进行智能分析和报告生成。
*   **🔌 自动发现**: 编写任务脚本即插即用，框架自动扫描并注册任务。
*   **🐍 Python 优先**: 纯 Python 实现，易于扩展和维护。
*   **📝 双语注释**: 核心代码全中文/英文双语注释，降低源码阅读门槛。

## 👤 作者信息

*   **作者**: 凌封
*   **网站**: [AI全书](https://aibook.ren)

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install playwright pyyaml
playwright install
```

### 2. 启动浏览器
使用内置脚本一键启动开启了远程调试端口的 Chrome：
```bash
python launch_browser.py
```
*(注意：请在弹出的浏览器窗口中登录你需要访问的网站)*

### 3. 运行示例任务

框架自带了两个浏览 [Linux.do](https://linux.do) 论坛的示例任务，可用于完成社区日常阅读任务：

#### 📖 示例一：刷主题阅读数
自动浏览"开发"分类下的话题，滚动页面收集话题链接并逐一访问，完成主题阅读数任务。
```bash
python main.py --task linux_do
```
在 `config/settings.yaml` 中可配置目标主题数：
```yaml
tasks:
  linux_do_target_count: 500    # 目标阅读主题数
```

#### 📝 示例二：刷帖子阅读数
从[热门话题排行榜](https://linux.do/hot?order=posts)（按帖子数排序）中，跳过前 N 个话题，逐一进入后续话题并模拟真实用户行为滚动阅读帖子（渐进式滚动、随机停顿、偶尔回滚等），完成帖子阅读数任务。
```bash
python main.py --task linux_do_posts
```
在 `config/settings.yaml` 中可配置参数：
```yaml
tasks:
  linux_do_posts_target_count: 10000  # 目标阅读帖子数
  linux_do_posts_skip_top: 3         # 跳过前 N 个热门话题
  linux_do_posts_read_time_min: 1    # 每个帖子最短阅读停顿（秒）
  linux_do_posts_read_time_max: 3    # 每个帖子最长阅读停顿（秒）
```

### 4. 配置文件说明 (可选)
框架会读取 `config/settings.yaml`。你可以修改它来适应你的环境（如 Chrome 路径、调试端口等）：
```yaml
chrome:
  executable_path: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
  debug_port: 9222
```

## 🛠️ 开发指南

### 创建新任务
在 `tasks/` 目录下创建一个新文件，例如 `my_task.py`，继承 `BaseTask` 即可：

```python
from framework.core.task_base import BaseTask

class MyTask(BaseTask):
    name = "my_task" # 命令行调用的名称

    def run(self):
        page = self.driver.get_page()
        page.goto("https://www.google.com")
        self.logger.info("Opened Google")
```

然后直接运行：
```bash
python main.py --task my_task
```

**提示：** `tasks/templates/task_template.py` 它是包含详细注释和 AI 示例的开发模板，建议直接复制该文件开始开发。

## 📂 目录结构

```text
auto-chrome/
├── framework/          # 核心框架代码
│   ├── core/           # 驱动、基类、上下文
│   ├── ai/             # AI Agent 接口
│   └── utils/          # 工具函数
├── tasks/              # 任务目录
│   ├── examples/       # 示例任务
│   └── templates/      # 任务模板
├── config/             # 配置文件
├── launch_browser.py   # 浏览器启动器
└── main.py             # 主入口
```

## 🤝 贡献
欢迎提交 Issue 和 Pull Request！

## 📄 许可证
MIT License

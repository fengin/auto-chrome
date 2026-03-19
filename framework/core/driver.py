# https://aibook.ren (AI全书)
import time
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from typing import Optional
from framework.core.context import Context

class BrowserDriver:
    def __init__(self, context: Context):
        self.context = context
        self.logger = context.get_logger("BrowserDriver")
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.browser_context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self):
        """
        Initializes Playwright and connects to the browser.
        初始化 Playwright 并连接到浏览器。
        """
        self.logger.info("Initializing Playwright...")
        self.playwright = sync_playwright().start()
        
        # Access config / 获取配置
        cdp_port = self.context.config.chrome.get("debug_port", 9222)
        cdp_url = f"http://127.0.0.1:{cdp_port}"
        
        # Connect logic with retry / 连接逻辑（带重试）
        max_retries = 10
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Connecting to CDP at {cdp_url} (Attempt {attempt+1}/{max_retries})...")
                self.browser = self.playwright.chromium.connect_over_cdp(cdp_url)
                
                # 智能选择页面：从所有 context 的 pages 中找到合适的可见页面
                # Chrome 会话恢复时可能有多个标签页，直接取 pages[0] 可能拿到不可见的后台页面
                self.page = None
                self.browser_context = None

                for ctx in self.browser.contexts:
                    for p in ctx.pages:
                        url = p.url
                        # 跳过扩展页面、devtools 页面等不可见页面
                        if url.startswith("chrome-extension://") or url.startswith("devtools://"):
                            continue
                        # 优先选择有实际内容的页面（非 about:blank）
                        if self.page is None or (self.page.url == "about:blank" and url != "about:blank"):
                            self.page = p
                            self.browser_context = ctx

                # 如果没找到合适的页面，回退到默认行为
                if not self.page:
                    if self.browser.contexts:
                        self.browser_context = self.browser.contexts[0]
                    else:
                        self.browser_context = self.browser.new_context()
                    
                    if self.browser_context.pages:
                        self.page = self.browser_context.pages[0]
                    else:
                        self.page = self.browser_context.new_page()

                # 确保选中的页面在前台可见
                try:
                    self.page.bring_to_front()
                except Exception:
                    pass

                self.logger.info(f"Successfully connected to browser! Active page: {self.page.url}")
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"Failed to connect after {max_retries} attempts. Error: {e}")
                    raise e
                time.sleep(2)

    def verify_turnstile(self):
         """
         Experimental: Check for basic turnstile/cloudflare checks and wait?
         Or just a placeholder for now.
         实验性功能：检查基本的 turnstile/cloudflare 验证并等待？
         目前仅作为占位符。
         """
         pass

    def close(self):
        """
        Closes the connection (but usually leaves browser running if CDP).
        关闭连接（如果是 CDP，通常保留浏览器运行）。
        """
        if self.browser:
            self.logger.info("Disconnecting from browser...")
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def get_page(self) -> Page:
        if not self.page:
            raise RuntimeError("Driver not started or page not available.")
        return self.page

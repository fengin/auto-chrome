# https://aibook.ren (AI全书)
import random
import time
from framework.core.task_base import BaseTask

class LinuxDoBrowserTask(BaseTask):
    name = "linux_do"

    def run(self):
        page = self.driver.get_page()
        
        target_category = "https://linux.do/c/develop/4"
        self.logger.info(f"Navigating to Category: {target_category} ...")
        page.goto(target_category)

        self.logger.info("\n" + "="*50)
        self.logger.info(" IMPORTANT: Please switch to the browser window and LOG IN if needed.")
        self.logger.info(" We are now in the 'Develop' category.")
        self.logger.info("="*50 + "\n")
        
        self.logger.info("Waiting 3 seconds before starting collection...")
        time.sleep(3)

        # Use config if available / 如果可用，使用配置
        target_count = self.context.config.tasks.get("linux_do_target_count", 100) 
        self.logger.info(f"Collecting topics from this category... target: {target_count}")
        topic_urls = set()
        
        no_new_data_count = 0
        last_height = 0
        
        while len(topic_urls) < target_count:
            # Get links - simplified selector logic
            # 获取链接 - 简化的选择器逻辑
            links = page.locator(".topic-list-item .main-link a.title").all()
            
            initial_count = len(topic_urls)
            
            for link in links:
                try:
                    url = link.get_attribute("href")
                    if url:
                        if url.startswith("/"):
                            url = "https://linux.do" + url
                        if "/t/" in url:
                             topic_urls.add(url)
                except Exception:
                    pass
            
            current_count = len(topic_urls)
            self.logger.info(f"Collected {current_count} unique topics so far...")
            
            if current_count >= target_count:
                break

            # Scroll logic / 滚动逻辑
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)

            # Check if we are stuck
            # 检查是否卡住（没有新内容加载）
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == last_height and current_count == initial_count:
                 no_new_data_count += 1
                 if no_new_data_count > 10:
                     self.logger.warning("No new content loaded after multiple attempts.")
                     break
            else:
                 no_new_data_count = 0
            
            last_height = current_height

        topics_list = list(topic_urls)[:target_count]
        random.shuffle(topics_list)
        
        self.logger.info(f"Successfully collected {len(topics_list)} topics. Starting FAST browse loop...")

        for i, url in enumerate(topics_list):
            self.logger.info(f"[{i+1}/{len(topics_list)}] Visiting: {url}")
            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                
                # Faster reading simulation
                # 更快的阅读模拟
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(random.randint(1000, 2000))
                
                page.mouse.wheel(0, -500)
                page.wait_for_timeout(random.randint(500, 1000))

            except Exception as e:
                self.logger.error(f"Error visiting {url}: {e}")
                continue

        self.logger.info("Finished browsing topics!")

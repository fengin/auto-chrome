# https://aibook.ren (AI全书)
import json
import os
import random
import re
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

        # 加载已读话题历史记录
        self._load_history()
        self.logger.info(f"已加载历史记录，共有 {len(self.visited_topics)} 个已读话题")

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

        # 过滤已读话题
        new_topics = [url for url in topics_list if self._get_topic_base(url) not in self.visited_topics]
        self.logger.info(f"共收集 {len(topics_list)} 个话题，其中 {len(new_topics)} 个未读")

        if not new_topics:
            self.logger.info("所有话题均已读过，任务结束")
            return

        random.shuffle(new_topics)
        
        self.logger.info(f"Starting FAST browse loop with {len(new_topics)} new topics...")

        for i, url in enumerate(new_topics):
            self.logger.info(f"[{i+1}/{len(new_topics)}] Visiting: {url}")
            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                
                # Faster reading simulation
                # 更快的阅读模拟
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(random.randint(1000, 2000))
                
                page.mouse.wheel(0, -500)
                page.wait_for_timeout(random.randint(500, 1000))

                # 记录已读并保存
                self.visited_topics.add(self._get_topic_base(url))
                self._save_history()

            except Exception as e:
                self.logger.error(f"Error visiting {url}: {e}")
                continue

        self.logger.info(f"Finished browsing topics! 共浏览 {len(new_topics)} 个新话题")

    def _get_history_path(self):
        """获取历史记录文件路径（与任务脚本同目录）"""
        return os.path.join(os.path.dirname(__file__), ".linux_do_history.json")

    def _load_history(self):
        """从 JSON 文件加载已读话题历史记录"""
        self.visited_topics = set()
        path = self._get_history_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.visited_topics = set(json.load(f))
            except Exception as e:
                self.logger.warning(f"加载历史记录失败: {e}")

    def _save_history(self):
        """将已读话题历史记录保存到 JSON 文件"""
        try:
            with open(self._get_history_path(), "w", encoding="utf-8") as f:
                json.dump(list(self.visited_topics), f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"保存历史记录失败: {e}")

    @staticmethod
    def _get_topic_base(url):
        """提取话题基础路径（去掉末尾页码）"""
        return re.sub(r'/\d+$', '', url)

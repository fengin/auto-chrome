# https://aibook.ren (AI全书)
import random
import time
from framework.core.task_base import BaseTask

class LinuxDoBrowserTask(BaseTask):
    name = "linux_do"

    def run(self):
        page = self.driver.get_page()
        
        # 从配置读取入口 URL 列表，支持多个
        entry_urls = self.context.config.tasks.get("linux_do_entry_urls", ["https://linux.do/c/develop/4"])
        if isinstance(entry_urls, str):
            entry_urls = [entry_urls]

        target_count = self.context.config.tasks.get("linux_do_target_count", 100) 
        self.logger.info(f"入口页面共 {len(entry_urls)} 个，目标阅读主题数: {target_count}")
        
        time.sleep(3)

        topic_urls = []
        
        # 遍历每个入口 URL，只收集有小蓝点（未读）的话题
        for entry_idx, entry_url in enumerate(entry_urls):
            if len(topic_urls) >= target_count:
                break

            self.logger.info(f"[入口 {entry_idx+1}/{len(entry_urls)}] 导航到: {entry_url}")
            page.goto(entry_url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)

            no_new_data_count = 0
            last_height = 0
            seen_urls = set(url for url in topic_urls)
            
            while len(topic_urls) < target_count:
                rows = page.locator("tr.topic-list-item").all()
                initial_count = len(topic_urls)
                
                for row in rows:
                    try:
                        # 检查是否有小蓝点（新话题标记）
                        new_badge = row.locator(".badge.new-topic")
                        if new_badge.count() == 0:
                            continue

                        # 获取话题链接
                        link = row.locator("a.title").first
                        href = link.get_attribute("href")
                        if href:
                            if href.startswith("/"):
                                href = "https://linux.do" + href
                            if "/t/" in href and href not in seen_urls:
                                topic_urls.append(href)
                                seen_urls.add(href)
                    except Exception:
                        pass
                
                current_count = len(topic_urls)
                self.logger.info(f"已收集 {current_count} 个未读话题...")
                
                if current_count >= target_count:
                    break

                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

                current_height = page.evaluate("document.body.scrollHeight")
                if current_height == last_height and current_count == initial_count:
                     no_new_data_count += 1
                     if no_new_data_count > 10:
                         self.logger.info(f"当前入口页面已无更多内容，切换下一个入口")
                         break
                else:
                     no_new_data_count = 0
                
                last_height = current_height

        topics_list = topic_urls[:target_count]

        if not topics_list:
            self.logger.info("没有未读话题，任务结束")
            return

        random.shuffle(topics_list)
        self.logger.info(f"共收集到 {len(topics_list)} 个未读话题，开始浏览...")

        for i, url in enumerate(topics_list):
            self.logger.info(f"[{i+1}/{len(topics_list)}] Visiting: {url}")
            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                
                # 阅读模拟
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(random.randint(1000, 2000))
                
                page.mouse.wheel(0, -500)
                page.wait_for_timeout(random.randint(500, 1000))

            except Exception as e:
                self.logger.error(f"Error visiting {url}: {e}")
                continue

        self.logger.info(f"任务完成！共浏览 {len(topics_list)} 个未读话题")

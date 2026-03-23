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
        
        topics_read = 0

        for entry_idx, entry_url in enumerate(entry_urls):
            if topics_read >= target_count:
                break

            self.logger.info(f"\n[入口 {entry_idx+1}/{len(entry_urls)}] 导航到: {entry_url}")
            page.goto(entry_url, timeout=30000, wait_until="load")
            time.sleep(3)

            # 在当前入口列表页中寻找未读话题并逐一点击浏览
            read_in_entry = self._browse_unread_in_list(page, entry_url, target_count - topics_read)
            topics_read += read_in_entry
            self.logger.info(f"入口 {entry_idx+1} 完成，本入口阅读 {read_in_entry} 个，累计: {topics_read}/{target_count}")

        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"任务完成！共阅读 {topics_read} 个话题")
        self.logger.info(f"{'='*50}")

    def _browse_unread_in_list(self, page, entry_url, remaining):
        """
        在当前话题列表页中：
        1. 寻找带小蓝点的未读话题
        2. 点击标题进入话题
        3. 模拟滚动浏览
        4. 重新导航回列表（释放内存），继续下一个
        5. 连续下拉 3 次无新未读话题则返回
        """
        read_count = 0
        visited_titles = set()  # 记录已点击的话题标题，避免重复
        no_new_rounds = 0

        while read_count < remaining:
            # 等待列表加载
            try:
                page.wait_for_selector("tr.topic-list-item", timeout=10000)
            except Exception:
                self.logger.warning("未找到话题列表")
                break

            # 在当前可见的列表中寻找未读话题
            found_unread = False
            rows = page.locator("tr.topic-list-item").all()

            for row in rows:
                try:
                    # 检查是否有小蓝点
                    if row.locator(".badge.new-topic").count() == 0:
                        continue

                    # 获取话题标题，避免重复点击
                    title_el = row.locator("a.title").first
                    title_text = title_el.text_content() or ""
                    if title_text in visited_titles:
                        continue

                    visited_titles.add(title_text)
                    found_unread = True
                    no_new_rounds = 0

                    self.logger.info(f"  [{read_count+1}] 点击未读话题: {title_text[:50]}...")

                    # 先滚动到该话题可见位置
                    title_el.scroll_into_view_if_needed()
                    time.sleep(0.5)

                    # 模拟人工点击话题标题
                    title_el.click()
                    time.sleep(random.uniform(2, 3))  # 等待页面加载和 Discourse 初始化

                    # 模拟阅读：分步滚动
                    self._simulate_reading(page)

                    read_count += 1

                    if read_count >= remaining:
                        break

                    # 重新导航回列表页（释放话题页面内存，避免累积）
                    self.logger.info(f"  返回列表...")
                    page.goto(entry_url, timeout=30000, wait_until="load")
                    time.sleep(random.uniform(2, 3))

                except Exception as e:
                    self.logger.error(f"  处理话题出错: {e}")
                    # 尝试回到列表
                    try:
                        page.goto(entry_url, timeout=30000, wait_until="load")
                        time.sleep(2)
                    except Exception:
                        pass
                    continue

            if read_count >= remaining:
                break

            if not found_unread:
                # 当前可见列表没有未读话题，下拉加载更多
                no_new_rounds += 1
                if no_new_rounds >= 3:
                    self.logger.info(f"  连续 {no_new_rounds} 次下拉无新未读话题，切换下一个入口")
                    break

                self.logger.info(f"  当前列表无新未读话题，下拉加载更多（第 {no_new_rounds} 次）...")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

        return read_count

    def _simulate_reading(self, page):
        """模拟人工阅读行为：分步滚动 + 停顿 + 等待 timings 请求"""
        # 分步滚动
        for _ in range(random.randint(3, 5)):
            page.mouse.wheel(0, random.randint(300, 600))
            time.sleep(random.uniform(1, 2))

        # 偶尔回滚
        if random.random() < 0.5:
            page.mouse.wheel(0, -random.randint(200, 400))
            time.sleep(random.uniform(0.5, 1))

        # 等待 Discourse timings 请求发出完成（关键！）
        time.sleep(3)

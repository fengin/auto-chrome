# https://aibook.ren (AI全书)
import json
import os
import random
import re
import time
from framework.core.task_base import BaseTask


class LinuxDoPostsBrowserTask(BaseTask):
    """
    刷贴子数任务：从热门话题排行（按贴子数排序）中，
    跳过前 N 个话题，逐一进入剩余话题并模拟阅读帖子，
    完成指定数量的帖子阅读任务。
    """
    name = "linux_do_posts"

    def run(self):
        page = self.driver.get_page()

        # 读取配置 / Read config
        target_posts = self.context.config.tasks.get("linux_do_posts_target_count", 100)
        skip_top = self.context.config.tasks.get("linux_do_posts_skip_top", 3)
        self.read_time_min = self.context.config.tasks.get("linux_do_posts_read_time_min", 2)
        self.read_time_max = self.context.config.tasks.get("linux_do_posts_read_time_max", 5)

        # 点赞配置
        self.like_min_chars = self.context.config.tasks.get("linux_do_posts_like_min_chars", 50)
        self.like_max_count = self.context.config.tasks.get("linux_do_posts_like_max_count", 30)
        self.total_likes = 0  # 已点赞计数

        self.logger.info(f"目标阅读帖子数: {target_posts}, 跳过前 {skip_top} 个热门话题")
        self.logger.info(f"点赞策略: 帖子中文字数 >= {self.like_min_chars} 时点赞，上限 {self.like_max_count} 个")

        # 加载已读主题历史记录
        self._load_history()
        self.logger.info(f"已加载历史记录，共有 {len(self.visited_topics)} 个已读主题")

        # 将页面带到前台，确保用户可以看到操作
        page.bring_to_front()

        # Step 1: 导航到热门话题页面（按帖子数排序）
        hot_url = "https://linux.do/hot?order=posts"
        self.logger.info(f"导航到热门话题页面: {hot_url}")
        page.goto(hot_url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(3)

        # Step 2: 收集话题链接（跳过前 N 个）
        topic_urls = self._collect_topics(page, skip_top)

        if not topic_urls:
            self.logger.warning("未收集到任何话题链接，任务结束")
            return

        # 过滤已读主题
        new_topic_urls = [url for url in topic_urls if self._get_topic_base(url) not in self.visited_topics]
        self.logger.info(f"共收集到 {len(topic_urls)} 个话题（已跳过前 {skip_top} 个），其中 {len(new_topic_urls)} 个未读")

        if not new_topic_urls:
            self.logger.info("所有话题均已读过，任务结束")
            return

        topic_urls = new_topic_urls

        # Step 3: 逐一浏览话题中的帖子
        total_read = 0
        for i, topic_url in enumerate(topic_urls):
            if total_read >= target_posts:
                self.logger.info(f"已达到目标阅读帖子数 {target_posts}，停止浏览")
                break

            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"[话题 {i+1}/{len(topic_urls)}] 进入: {topic_url}")
            self.logger.info(f"当前累计已阅读帖子: {total_read}/{target_posts}")

            try:
                posts_read = self._browse_topic_posts(page, topic_url, target_posts - total_read)
                total_read += posts_read
                self.logger.info(f"本话题阅读了 {posts_read} 个帖子，累计: {total_read}/{target_posts}")

                # 记录已读主题并保存
                self.visited_topics.add(self._get_topic_base(topic_url))
                self._save_history()
            except Exception as e:
                self.logger.error(f"浏览话题出错: {e}")
                continue

            # 话题间间隔：模拟用户思考选择下一个话题
            if total_read < target_posts:
                wait_time = random.uniform(3, 6)
                self.logger.info(f"话题间停顿 {wait_time:.1f} 秒...")
                time.sleep(wait_time)

        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"任务完成！共阅读 {total_read} 个帖子，点赞 {self.total_likes} 个")
        self.logger.info(f"{'='*50}")

    def _get_history_path(self):
        """获取历史记录文件路径（与任务脚本同目录）"""
        return os.path.join(os.path.dirname(__file__), ".linux_do_posts_history.json")

    def _load_history(self):
        """从 JSON 文件加载已读主题历史记录"""
        self.visited_topics = set()
        path = self._get_history_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.visited_topics = set(json.load(f))
            except Exception as e:
                self.logger.warning(f"加载历史记录失败: {e}")

    def _save_history(self):
        """将已读主题历史记录保存到 JSON 文件"""
        try:
            with open(self._get_history_path(), "w", encoding="utf-8") as f:
                json.dump(list(self.visited_topics), f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"保存历史记录失败: {e}")

    @staticmethod
    def _get_topic_base(url):
        """
        提取主题基础路径（去掉末尾页码），同一主题不同页面视为相同。
        例如: https://linux.do/t/topic/1697632/8 -> https://linux.do/t/topic/1697632
        """
        return re.sub(r'/\d+$', '', url)

    def _collect_topics(self, page, skip_top):
        """
        从热门话题页面收集话题 URL，跳过前 N 个。
        支持滚动加载更多话题。
        """
        topic_urls = []

        # 等待话题列表加载
        try:
            page.wait_for_selector("tr.topic-list-item", timeout=10000)
        except Exception:
            self.logger.error("未找到话题列表，请确认页面已正确加载且已登录")
            return topic_urls

        # 向下滚动几次以加载更多话题
        for scroll_round in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.5)

        # 回到页面顶部
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        # 获取所有话题行
        rows = page.locator("tr.topic-list-item").all()
        self.logger.info(f"页面上共有 {len(rows)} 个话题行")

        for idx, row in enumerate(rows):
            # 跳过前 N 个话题
            if idx < skip_top:
                try:
                    title = row.locator("a.title").first.text_content()
                    self.logger.info(f"  [跳过 #{idx+1}] {title}")
                except Exception:
                    self.logger.info(f"  [跳过 #{idx+1}]")
                continue

            try:
                link = row.locator("a.title").first
                href = link.get_attribute("href")
                if href:
                    if href.startswith("/"):
                        href = "https://linux.do" + href
                    if "/t/" in href:
                        topic_urls.append(href)
            except Exception:
                pass

        return topic_urls

    def _browse_topic_posts(self, page, topic_url, remaining_target):
        """
        进入单个话题，模拟人类行为滚动阅读帖子。
        返回本话题中阅读的帖子数。
        """
        page.goto(topic_url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(random.uniform(2, 3))

        posts_read = 0
        seen_post_ids = set()
        no_new_posts_count = 0
        long_pause_counter = random.randint(5, 8)  # 每阅读多少个帖子后长停顿

        while posts_read < remaining_target:
            # 统计当前可见的帖子
            post_elements = page.locator(".topic-post").all()
            new_posts_found = False

            for post_el in post_elements:
                try:
                    # 使用 article 的 data-post-id 或 id 来唯一标识帖子
                    article = post_el.locator("article").first
                    post_id = article.get_attribute("data-post-id") or article.get_attribute("id")

                    if post_id and post_id not in seen_post_ids:
                        seen_post_ids.add(post_id)
                        posts_read += 1
                        new_posts_found = True

                        # 尝试点赞
                        self._try_like_post(post_el)

                        if posts_read >= remaining_target:
                            break
                except Exception:
                    pass

            if posts_read >= remaining_target:
                break

            # 模拟人类滚动行为
            self._human_like_scroll(page)

            # 阅读停顿：每次滚动后随机暂停（可配置）
            read_time = random.uniform(self.read_time_min, self.read_time_max)
            time.sleep(read_time)

            # 随机鼠标微动
            if random.random() < 0.4:
                self._random_mouse_move(page)

            # 长停顿：每阅读若干帖子后插入 5~10 秒停顿
            if posts_read > 0 and posts_read % long_pause_counter == 0:
                long_pause = random.uniform(5, 10)
                self.logger.info(f"  长停顿 {long_pause:.1f} 秒（已阅读 {posts_read} 个帖子）")
                time.sleep(long_pause)
                long_pause_counter = random.randint(5, 8)

            # 偶尔回滚：~15% 概率向上回滚一小段
            if random.random() < 0.15:
                scroll_back = random.randint(100, 300)
                self.logger.info(f"  回滚 {scroll_back}px（模拟回看）")
                page.mouse.wheel(0, -scroll_back)
                time.sleep(random.uniform(1, 2))

            # 检查是否已无新帖子可加载（到达底部）
            if not new_posts_found:
                no_new_posts_count += 1
                if no_new_posts_count >= 5:
                    self.logger.info(f"  话题帖子已全部浏览完（共 {posts_read} 个）")
                    break
            else:
                no_new_posts_count = 0

        return posts_read

    def _try_like_post(self, post_el):
        """
        尝试为帖子点赞：
        - 帖子内容中文字数 >= like_min_chars 时才点赞
        - 已点赞数达到 like_max_count 时停止
        - 已经点过赞的帖子不重复点赞
        """
        if self.total_likes >= self.like_max_count:
            return

        try:
            # 获取帖子文本内容
            content_el = post_el.locator(".cooked").first
            if not content_el.is_visible():
                return

            text = content_el.text_content() or ""
            # 统计中文字符数
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

            if chinese_chars < self.like_min_chars:
                return

            # 70% 概率点赞，30% 概率跳过，避免点赞过于频繁
            if random.random() > 0.7:
                return

            # 查找点赞按钮（兼容多种 Discourse 版本和插件）
            # 依次尝试: 标准按钮 > reactions 插件按钮 > 包含心形图标的按钮
            like_btn = None
            for selector in [
                "button.toggle-like",
                "button.like-count",
                ".discourse-reactions-reaction-button",
                "button[class*='like']",
            ]:
                btn = post_el.locator(selector).first
                try:
                    if btn.is_visible(timeout=500):
                        like_btn = btn
                        break
                except Exception:
                    continue

            if not like_btn:
                return

            # 检查是否已点过赞（已点赞的按钮有 has-like / my-likes / liked 类名）
            btn_class = like_btn.get_attribute("class") or ""
            if any(kw in btn_class for kw in ["has-like", "my-likes", "liked"]):
                return

            # 点赞
            like_btn.click()
            self.total_likes += 1
            self.logger.info(f"  👍 点赞！（中文字数: {chinese_chars}, 已点赞: {self.total_likes}/{self.like_max_count}）")

            # 点赞后短暂停顿，模拟自然行为
            time.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            # 点赞失败不影响主流程
            pass

    def _human_like_scroll(self, page):
        """
        模拟人类渐进式滚动：每次滚动 300~600px 随机距离。
        """
        scroll_distance = random.randint(300, 600)
        page.mouse.wheel(0, scroll_distance)
        # 短暂等待页面渲染
        time.sleep(random.uniform(0.3, 0.8))

    def _random_mouse_move(self, page):
        """
        随机鼠标微动：模拟用户在阅读时的自然鼠标移动。
        """
        try:
            viewport_width = page.viewport_size.get("width", 1280) if page.viewport_size else 1280
            viewport_height = page.viewport_size.get("height", 800) if page.viewport_size else 800

            target_x = random.randint(100, viewport_width - 100)
            target_y = random.randint(100, viewport_height - 100)
            page.mouse.move(target_x, target_y)
            time.sleep(random.uniform(0.1, 0.3))
        except Exception:
            pass

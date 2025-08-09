import feedparser
import re


class RSSParser:

    def __init__(self, config):
        self.config = config
        default_resource = next(
            (res for res in config["resources"] if res["name"] == config["default"]),
            None
        )
        if not default_resource:
            raise ValueError(f"未找到默认资源: {config["default"]}")
        self.base_url = default_resource["url"]
        self.connect_word = default_resource["connect_word"]

    # 生成关键词搜索链接
    def __generate_search_url(self, keywords: tuple) -> str:
        search_url = self.base_url + self.connect_word.join(keywords)
        print("Searching URL: " + search_url)
        return search_url

    # 解析 RSS
    @staticmethod
    def __parse_rss(feed_url: str) -> feedparser.FeedParserDict:
        feed = feedparser.parse(feed_url)
        return feed

    # 获取特定的动画列表
    @classmethod
    def __get_anime_list(cls, feed: feedparser.FeedParserDict) -> list:
        anime_list = []
        for idx, entry in enumerate(feed.entries):
            download_link = None

            # 遍历所有 links，找 type 为 'application/x-bittorrent' 或 rel 为 'enclosure' 的链接
            for link in entry.links:
                if "href" in link and (
                        link.get("type") == "application/x-bittorrent" or
                        link.get("rel") == "enclosure" or
                        link.get("href", "").startswith("magnet:")
                ):
                    download_link = link["href"]
                    break

            # 如果没找到下载链接就跳过
            if not download_link:
                continue

            anime_list.append({
                "id": idx,
                "title": cls.__sanitize_filename(entry.title),
                "download_link": download_link
            })

        return anime_list

    # 去除 Windows 下的非法字符
    @staticmethod
    def __sanitize_filename(filename: str) -> str:
        return re.sub(r"[\\/:*?\"<>|]", " ", filename)

    # 根据关键词获得指定动画列表
    def get_anime_list(self, *keywords) -> list:
        if len(keywords) == 1 and isinstance(keywords[0], list):
            keywords = keywords[0]
        search_url = self.__generate_search_url(keywords)
        feed = self.__parse_rss(search_url)
        return self.__get_anime_list(feed)

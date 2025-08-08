import feedparser
import re


class RSSParser:
    feed_dmhy_base_url = "https://www.dmhy.org/topics/rss/rss.xml"

    # 生成关键词搜索链接，适用于 dmhy
    @staticmethod
    def __generate_search_url(base_url: str, keywords: tuple) -> str:
        search_url = base_url + "?keyword=" + "+".join(keywords)
        print("Searching URL: " + search_url)
        return search_url

    # 解析 RSS
    @staticmethod
    def __parse_rss(feed_url: str) -> feedparser.FeedParserDict:
        feed = feedparser.parse(feed_url)
        return feed

    # 获取特定的动画列表
    @staticmethod
    def __get_anime_list(feed: feedparser.FeedParserDict) -> list:
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
                "title": RSSParser.__sanitize_filename(entry.title),
                "download_link": download_link
            })

        return anime_list

    # 去除 Windows 下的非法字符
    @staticmethod
    def __sanitize_filename(filename: str) -> str:
        return re.sub(r"[\\/:*?\"<>|]", " ", filename)

    # 根据关键词获得指定动画列表
    @staticmethod
    def get_anime_list(*keywords) -> list:
        if len(keywords) == 1 and isinstance(keywords[0], list):
            keywords = keywords[0]
        search_url = RSSParser.__generate_search_url(RSSParser.feed_dmhy_base_url, keywords)
        feed = RSSParser.__parse_rss(search_url)
        return RSSParser.__get_anime_list(feed)

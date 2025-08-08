from RSSParser import RSSParser
import qbittorrentapi

class Downloader:
    parser = RSSParser()

    # 调用本地 qBitTorrent 下载
    @staticmethod
    def download_anime(anime, path: str = None) -> None:
        # qbt = qbittorrentapi.Client(host="127.0.0.1", port=8080, username="admin", password="123123")
        # qbt.auth_log_in()
        # qbt.torrents_add(anime["download_link"], save_path=path)
        print("Downloading anime \"" + anime["title"] + "\"")
        print("Link: " + anime["download_link"])



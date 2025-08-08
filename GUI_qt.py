import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from RSSParser import RSSParser
from Downloader import Downloader


class SearchThread(QThread):
    results_ready = pyqtSignal(list)

    def __init__(self, keywords):
        super().__init__()
        self.keywords = keywords

    def run(self):
        anime_list = RSSParser().get_anime_list(self.keywords)
        self.results_ready.emit(anime_list)


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anime Manager")
        self.resize(1600, 900)

        self.results_per_page = 30
        self.current_page = 1
        self.anime_list = []
        self.isSearching = False

        # 主容器
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("输入搜索关键词...")
        self.entry.returnPressed.connect(self.start_search)

        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.start_search)

        search_layout.addWidget(self.entry)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)

        # 滚动结果区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout(self.result_widget)
        self.result_layout.addStretch()

        self.scroll_area.setWidget(self.result_widget)
        main_layout.addWidget(self.scroll_area)

        # 分页栏
        pagination_layout = QHBoxLayout()
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn = QPushButton("上一页")
        self.prev_btn.clicked.connect(self.prev_page)

        self.page_info = QLabel("第 0 / 0 页 | 共 0 条结果")

        self.next_btn = QPushButton("下一页")
        self.next_btn.clicked.connect(self.next_page)

        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_info)
        pagination_layout.addWidget(self.next_btn)

        main_layout.addLayout(pagination_layout)

        # 样式美化
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 16px;
                border: 2px solid #ccc;
                border-radius: 6px;
            }
            QPushButton {
                padding: 8px 16px;
                font-size: 16px;
                background-color: #4CAF50;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 16px;
            }
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)

    def start_search(self):
        if self.isSearching:
            return
        self.isSearching = True
        self.anime_list.clear()
        self.current_page = 1
        self.clear_results()

        keywords = self.entry.text().strip().split()
        if not keywords:
            self.isSearching = False
            return

        # 搜索提示
        searching_label = QLabel("🔍 正在搜索，请稍候...")
        self.result_layout.insertWidget(0, searching_label)

        self.search_btn.setEnabled(False)
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)

        self.search_thread = SearchThread(keywords)
        self.search_thread.results_ready.connect(self.on_results_ready)
        self.search_thread.start()

    def on_results_ready(self, results):
        self.anime_list = results
        self.isSearching = False
        self.search_btn.setEnabled(True)
        self.prev_btn.setEnabled(True)
        self.next_btn.setEnabled(True)
        self.show_page()

    def clear_results(self):
        while self.result_layout.count() > 1:
            item = self.result_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_page(self):
        self.clear_results()

        if not self.anime_list:
            no_label = QLabel("❌ 没有找到结果")
            self.result_layout.insertWidget(0, no_label)
            self.page_info.setText("第 0 / 0 页 | 共 0 条结果")
            return

        total_results = len(self.anime_list)
        total_pages = (total_results + self.results_per_page - 1) // self.results_per_page
        self.current_page = max(1, min(self.current_page, total_pages))

        start_idx = (self.current_page - 1) * self.results_per_page
        end_idx = start_idx + self.results_per_page

        for anime in self.anime_list[start_idx:end_idx]:
            self.display_card(anime)

        self.page_info.setText(f"第 {self.current_page} / {total_pages} 页 | 共 {total_results} 条结果")

    def display_card(self, anime):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card_layout = QHBoxLayout(card)

        # 标题
        title_label = QLabel(anime["title"])
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title_label.setWordWrap(True)  # 自动换行，避免太长溢出

        # 按钮
        download_btn = QPushButton("下载")
        download_btn.clicked.connect(lambda _, a=anime: Downloader.download_anime(a))

        # 加入布局
        card_layout.addWidget(title_label)
        card_layout.addWidget(download_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.result_layout.insertWidget(self.result_layout.count() - 1, card)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.show_page()

    def next_page(self):
        total_results = len(self.anime_list)
        total_pages = (total_results + self.results_per_page - 1) // self.results_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.show_page()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec())

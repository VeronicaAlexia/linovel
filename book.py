import json
import os

import api


class Book:
    def __init__(self, book_info: dict):
        self.content_config = []
        self.book_info = book_info
        self.book_name = api.illegal_strip(book_info['bookName'])
        self.book_author = book_info['authorName']
        self.cover = book_info['bookCoverUrl']
        self.chapter_url_list = book_info['chapUrl']
        self.save_config_path = os.path.join("Cache", self.book_name + ".json")
        self.out_text_path = os.path.join("downloads", self.book_name)

    def init_content_config(self):
        if not os.path.exists("Cache"):
            os.mkdir("Cache")
        if not os.path.exists(self.out_text_path):
            os.makedirs(self.out_text_path)
        if os.path.exists(self.save_config_path):
            self.content_config = api.read_text(self.save_config_path, json_load=True)
            if self.content_config is None:
                self.content_config = []
        else:
            self.content_config = []
        show_info = "book name: {}\nauthor: {}\nchapter count: {}\n\n".format(
            self.book_name, self.book_author, len(self.chapter_url_list))
        print(show_info)
        api.write_text(path_name=os.path.join(self.out_text_path, self.book_name + ".txt"), content=show_info)

    def save_content_json(self):
        try:
            json_info = json.dumps(self.content_config, ensure_ascii=False)
            api.write_text(path_name=self.save_config_path, content=json_info, mode="w")
        except Exception as err:
            print("save content json error: {}".format(err))

    def merge_text_file(self):
        self.content_config.sort(key=lambda x: x.get('chapterIndex'))
        for chapter_info in self.content_config:
            chapter_title = "第{}章: {}\n".format(chapter_info['chapterIndex'], chapter_info['chapterTitle'])
            chapter_content = '\n'.join(["　　" + i for i in chapter_info.get('chapterContent').split("\n")])
            api.write_text(
                path_name=os.path.join(self.out_text_path, self.book_name + ".txt"),
                content=chapter_title + chapter_content + "\n\n\n", mode="a")
        self.content_config.clear()

    def test_config_chapter(self, chapter_url: str):
        for i in self.content_config:
            if i.get("chapter_url") == chapter_url:
                return True

    def download_book(self):
        for index, chapter_url in enumerate(self.chapter_url_list, start=1):
            if not self.test_config_chapter(chapter_url):
                try:
                    chapter_info = api.get_chapter_info(chapter_url, index)
                    if isinstance(chapter_info, dict):
                        self.content_config.append(chapter_info)
                        print("{}/{} title:{}".format(
                            index, len(self.chapter_url_list), chapter_info.get('chapterTitle')), end="\r")
                except Exception as e:
                    print("error: {}".format(e), self.save_content_json())
            # else:
            # print("the chapter {} is already downloaded".format(chapter_url))

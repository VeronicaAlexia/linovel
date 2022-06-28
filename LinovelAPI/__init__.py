from HttpUtil import *


def get_book_info(book_id: str, retry: int = 0) -> [dict, None]:  # get book info from url by book_id
    response = get(api_url="https://www.linovel.net/book/{}.html".format(book_id), retry=retry)
    if response is not None and isinstance(response, str):  # if the response is not None and is a string
        html_str = etree.HTML(response)  # parse html string to lxml.etree.ElementTree
        return book_info_json(
            book_id=book_id,
            book_name=html_str.xpath('//h1[@class="book-title"]')[0].text,
            author_name=html_str.xpath('//div[@class="author-frame"]//a')[0].text,
            chapter_url_list=[i.get('href') for i in html_str.xpath('//div[@class="chapter"]/a')],
            cover_url=html_str.xpath('//div[@class="book-cover"]/a')[0].get('href'),
        )  # get book info from html string and return a dict with book info
    else:
        if retry <= 10 and response != 404:
            return get_book_info(book_id, retry + 1)
        return print("get book info failed, book_id is {}".format(book_id))


def get_chapter_info(chapter_url: str, index: int, content: str = "", retry: int = 0) -> [dict, None]:
    response = get(api_url="https://www.linovel.net" + chapter_url, retry=retry)
    if response is not None and isinstance(response, str):
        content_string = etree.HTML(response)
        for book in content_string.xpath('//div[@class="article-text"]/p'):
            if book.text is not None and len(book.text.strip()) != 0:
                content += book.text.strip() + "\n"
        return chapter_info_json(
            index=index, url=chapter_url, content=content,
            title=content_string.xpath('//div[@class="article-title"]')[0].text.strip(),
            image_list=get_chapter_cover(content_string)
        )  # return a dict with chapter info
    else:
        if retry <= 10:
            return get_chapter_info(chapter_url, index, content, retry + 1)
        return print("get chapter info failed, chapter_url is {}".format(chapter_url))


def get_sort(tag_name: str, page: int, retry: int = 0):  # get sort from url by page
    params = {"sort": "words", "sign": "-1", "page": page}
    response = get(api_url="https://www.linovel.net/cat/-1.html", params=params, retry=retry)
    if response is not None and isinstance(response, str):
        sort_list = [i.get('href').split('/')[-1][:-5] for i in etree.HTML(response).xpath('//a[@class="book-name"]')]
        if len(sort_list) != 0:
            return sort_list
    else:
        if retry <= 10:
            return get_sort(tag_name, page, retry + 1)
        return print("get sort failed, page is {}".format(page))


def search_book(book_name: str) -> [list, None]:
    response = get(api_url="https://www.linovel.net/search/", params={"kw": book_name})
    if response is not None and isinstance(response, str):
        html_str = response.split('<div class="rank-book-list">')[1]
        book_id_list = re.findall(r'<a href="/book/(\d+).html"', str(html_str))
        if len(book_id_list) != 0:
            return book_id_list
        else:
            return []
        # print(book_id)


def get_chapter_cover(html_string: [str, etree.ElementTree]) -> [list, None]:
    img_url_list = [
        img_url.get('src') for img_url in html_string.xpath('//div[@class="article-text"]//img')
    ]
    if isinstance(img_url_list, list) and len(img_url_list) != 0:
        return img_url_list
    else:
        return []

import requests
import bs4
import eel
from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
from typing import List

base_url = 'https://prodota.ru/forum/topic/'


@dataclass_json
@dataclass
class Post:
    author: str
    local_id: int
    url: str
    page_num: int
    bolds: List[str] = field(default_factory=list)


@eel.expose
def parse_topic(topic_id, page_from=1):
    current_page = int(page_from)
    posts = list()
    while 1:
        print(current_page)  # debug na kolene
        page_posts = get_page_posts(topic_id, current_page)
        for p in page_posts:
            posts.append(p.to_dict())

        if len(page_posts) == 20:
            current_page += 1
        else:
            print({'current_page': current_page, 'posts': posts})
            return {'current_page': current_page, 'posts': posts}


@eel.expose
def get_post_bolds(post_content):
    bolds = list()
    if post_content.find("strong", recursive=True) or post_content.find("b", recursive=True):
        text = str(post_content)
        bolds.append(text[text.startswith('<p>\n') and len('<p>\n'):])
    return bolds


@eel.expose
def get_page_posts(topic_id, page_num):
    r = requests.get(f'{base_url}{topic_id}/page/{page_num}/')
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    posts = list()
    for post in soup.find_all("article"):
        author_nick = post.find('span', class_='defrelNickTopic').text.strip('\n')
        id_content = post.find('ul', class_='ipsList_inline ipsComment_tools')
        post_local_id = id_content.text.strip('\n\t\r').replace(' #', '')
        post_url = id_content.find('a', class_='ipsType_blendLinks')['href']
        topic_post = Post(author=author_nick, local_id=post_local_id, url=post_url, page_num=page_num)

        for c in post.find('div', class_='ipsType_normal ipsType_richText ipsContained'):
            if c.__class__ == bs4.element.Tag and c.name == 'p':
                topic_post.bolds.extend(get_post_bolds(c))
        posts.append(topic_post)

    return posts


eel.init('web')
eel.start('main.html')

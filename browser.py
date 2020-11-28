import sys
from collections import deque
from os import path, mkdir

import bs4
import requests
from colorama import init, Fore, Style


def download(domain):
    if not path.isdir(base_dir):
        mkdir(base_dir)

    url = build_url(domain)
    soup = bs4.BeautifulSoup(
        requests.get(url).content,
        'html.parser',
        parse_only=bs4.SoupStrainer(['p', 'a', 'ul', 'ol', 'li'])
    )

    text = build_text(soup)
    with open(path.join(base_dir, build_filename(url)), 'w') as f:
        f.write(text)

    return text


def build_text(node):
    is_bs = isinstance(node, bs4.BeautifulSoup)

    if is_bs or node.name in ('p', 'li', 'ul', 'ol'):
        sep = "\n" if is_bs or node.name in ('ul', 'ol') else " "
        return sep.join(filter(bool, [build_text(x).strip() for x in node.contents]))
    elif node.name == 'a':
        return Fore.BLUE + node.get_text() + Style.RESET_ALL
    elif node.name:
        return node.get_text().strip()
    else:
        return node.strip()


def build_url(domain):
    return domain if domain[:8] == 'https://' else 'https://' + domain


def build_filename(url):
    return url[8:].split('/')[0]


def load(filename):
    location = path.join(base_dir, filename)
    if not path.isfile(location):
        return None

    with open(location, 'r') as f:
        return f.read()


def go_back():
    if not history or history[-1] is None:
        return ""

    return load(history.pop())


def strip_website(domain):
    return domain.split(".")[0] if domain else None


init()
base_dir = sys.argv[1]
last_website = None
history = deque()

while True:
    website = input()
    if website == 'exit':
        break

    add_history = True
    if website == 'back':
        content = go_back()
        add_history = False
    elif '.' in website:
        content = download(website)
    else:
        content = load(website)

    if add_history and content:
        history.append(strip_website(last_website))
        last_website = website

    if content:
        print(content)
    elif content is None:
        print("Error: Incorrect URL")

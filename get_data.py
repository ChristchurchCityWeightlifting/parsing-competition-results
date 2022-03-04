import time

import requests
from bs4 import BeautifulSoup
from rich import print

URL = "https://www.weightlifting.nz/events/results"
HEADERS = {"content-type": "application/json; charset=UTF-8"}


def get_links(url, headers):
    links = []
    response = requests.get(url, headers)
    soup = BeautifulSoup(response.content, "html.parser")
    print(response.text)
    links = soup.findall("a")
    return links


def main():
    links = get_links(URL, HEADERS)
    print(links)


if __name__ == "__main__":
    main()

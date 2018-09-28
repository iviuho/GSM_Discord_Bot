import requests
from bs4 import BeautifulSoup

class WebCrawler:
    def get_html(self, url):
        response = requests.get(url)
        html = response.text
        return html

    def get_soup(self, url):
        html = self.get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        return soup

if __name__ == "__main__":
    pass

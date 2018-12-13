import requests
from bs4 import BeautifulSoup

class WebCrawler:
    def get_html(self, url):
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return None
        html = response.text
        return html

    def get_soup(self, url):
        html = self.get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def save_html(self, url):
        with open("save_html.html", "w") as f:
            f.write(self.get_html(url))

if __name__ == "__main__":
    pass

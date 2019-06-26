import datetime
import json
import logging
import re
import requests
from bs4 import BeautifulSoup

if __package__ is None or __package__ == "":
    from menu import Menu
    from school import School
else:
    from .menu import Menu
    from .school import School


formatter = logging.Formatter(
    "%(asctime)s:: %(message)s",
    "%Y/%m/%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

regex = re.compile(r"[가-힣&\s]+")


def save_to_json(result, name="result.json"):
    """
    딕셔너리를 JSON 파일로 저장한다.
    파일 이름을 지정하지 않을 시엔, 'result.json'으로 저장된다.

    result: dict
    저장하고자 하는 데이터
    """
    logger.info("Started saving json file as {}.".format(name))

    try:
        with open(name, "w", encoding="UTF-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(e)
    else:
        logger.info("Finished saving.")


class MenuParser:
    def __init__(self, school):
        self.school = school

    def get_menu(self, year=None, month=None):
        """
        해당 학교로부터 급식을 가져온다.
        year와 month가 모두 주어졌다면 해당하는 정보를 가져온다.
        주어지지 않았을 때에는 자동으로 가져오게 된다.

        year: int
        month: int
        """
        if year is None or month is None:
            today = datetime.date.today()
        else:
            today = datetime.date(year, month, 1)

        url = self.__create_url(today.year, today.month)
        page = self.__get_page(url)
        soup = BeautifulSoup(page, "html.parser")
        items = soup.select("#contents > div > table > tbody > tr > td > div")
        res = self.__parse_menu_list(items)

        return Menu(res, today)

    def __get_page(self, url):
        try:
            page = requests.get(url)
            page.encoding = "UTF-8"
        except Exception as e:
            logger.error(e)
            return None

        return page.text

    def __create_url(self, year, month):
        today = datetime.date(year, month, 1)

        url = "https://{}/sts_sci_md00_001.do?".format(self.school.region)
        url += "schulCode={}&".format(self.school.code)
        url += "schulCrseScCode={}&".format(self.school.type)
        url += "schulKndScCode={:02d}&".format(self.school.type)
        url += "ay={}&".format(today.year)
        url += "mm={:02d}".format(today.month)

        return url

    def __parse_menu_list(self, menu_list):
        result = {}

        for item in menu_list:
            index = None
            menu = {
                Menu.Time.BREAKFAST: [],
                Menu.Time.LUNCH: [],
                Menu.Time.DINNER: []
            }

            if item.contents:
                for text in item.strings:
                    if text.isdigit():
                        result[int(text)] = menu
                    else:
                        index = self.__set_index(index, text)
                        match_result = regex.match(text)

                    if index is not None and match_result:
                        menu[index].append(match_result.group())

        return result

    def __set_index(self, index, text):
        if text == "[조식]":
            return Menu.Time.BREAKFAST
        elif text == "[중식]":
            return Menu.Time.LUNCH
        elif text == "[석식]":
            return Menu.Time.DINNER
        else:
            return index


if __name__ == "__main__":
    school = School(School.Region.GWANGJU, School.Type.HIGH, "F100000120")
    parser = MenuParser(school)

    menu = parser.get_menu()
    save_to_json(menu.menu)

import datetime
import random
import re
import requests
from bs4 import BeautifulSoup

class HTMLGetter:
    def __init__(self, url):
        self.url = url

    def get_html(self):
        try:
            response = requests.get(self.url)
        except requests.exceptions.ConnectionError:
            return None
        html = response.text
        return html

    def get_soup(self):
        html = self.get_html()
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def save_html(self):
        with open("save_html.html", "w") as f:
            f.write(self.get_html())


class TimeCalculator:
    @staticmethod
    def get_next_meal_index(now):
        # 8시 0분, 13시 30분, 19시 30분
        # 각각 식사 시간이 끝나는 시각(분 단위로 환산함)
        meal_time = [480, 810, 1170]
        
        for i in range(len(meal_time)):
            if (now.hour * 60 + now.minute) < meal_time[i]:
                return i
        return len(meal_time)

    @staticmethod
    def get_next_day():
        today = datetime.datetime.today()
        return today + datetime.timedelta(
            int(TimeCalculator.get_next_meal_index(today) / 3))


class DataManager:
    @classmethod
    def get_command(cls, command, keyword=None):
        func = getattr(cls, "get_%s" % command, "%s 작업을 처리하는데 문제가 발생했습니다." % command)
        return func() if keyword == None else func(keyword)

    @staticmethod
    def get_hungry():
        today = TimeCalculator.get_next_day()
        next_meal = TimeCalculator.get_next_meal_index(today)
        item = ["아침", "점심", "저녁"]

        soup = HTMLGetter("http://www.gsm.hs.kr/xboard/board.php?tbnum=8&sYear=%s&sMonth=%s"
            % (today.year, today.month)).get_soup()

        try:
            info = soup.select("#xb_fm_list > div.calendar > ul > li > div > div.slider_food_list.slider_food%s.cycle-slideshow" % today.day)
            menuList = (info[0].find("div", {"data-cycle-pager-template" : "<a href=#none; class=today_food_on%s title=%s></a>"
                % (next_meal % 3 + 1, item[next_meal % 3])}).find("span", "content").text).split("\n")

            p = re.compile("(?!에너지)[가-힣&\\s]+") # 영양성분 문장을 제외하기 위한 정규표현식
            result = "".join("- %s\n" % p.match(i).group() for i in menuList if p.match(i))

            # result의 길이가 0이면
            if not len(result):
                raise Exception

            return result
        except:
            print("[오류] GSM Bot이 식단표를 받아올 수 없습니다.")
            return "%s 급식을 불러올 수 없습니다." % item[next_meal % 3]

    @staticmethod
    def get_calendar():
        today = datetime.datetime.today()

        soup = HTMLGetter("http://www.gsm.hs.kr/xboard/board.php?tbnum=4").get_soup()

        try:
            info = soup.select("#xb_fm_list > div.calendar > ul > li > dl")

            result = "```"
            for i in info:
                if not i.find("dd") == None:
                    text = i.text.replace("\n", "")
                    data = text.split("- ")

                    result += "%6s - %s\n" % (data[0], data[1])
                    for i in data[2:]:
                        result += "%7s - %s\n" % ("", i)
            result += "```"

            return result
        except AttributeError:
            print("[오류] GSM Bot이 학사일정을 불러올 수 없습니다.")
            return "%s년 %s월 학사일정을 불러올 수 없습니다." % (today.year, today.month)

    @staticmethod
    def get_image(keyword):
        soup = HTMLGetter("https://www.google.co.kr/search?hl=en&tbm=isch&q=%s"
            % keyword).get_soup()

        try:
            info = soup.find_all("img")
            index = random.randint(1, len(info)) # 구글 자체 이미지가 포함되어 있기 때문에 1부터 시작한다
            return info[index]["src"] # 이미지의 링크를 가져옴
        except:
            print("[오류] GSM Bot이 이미지를 가져올 수 없습니다.")
            return None


if __name__ == "__main__":
    pass
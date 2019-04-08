import random
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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


class DataManager:
    def get_nextDay(self):
        today = datetime.today()
        nextMeal = self.get_nextMeal(today) # 아침, 점심, 저녁, 다음 날 아침중에 어떤 식사를 불러와야 하는지를 나타내는 정수

        try:
            today = today.replace(day = today.day + int(nextMeal / 3)) # 다음 날 아침을 불러와야 한다면 today에 다음 날로 바꾼 datetime 객체를 넣음
        except ValueError: # 한 달의 마지막 날에서 1이 더해진다면 ValueError가 발생하므로 예외 처리
            try:
                today = today.replace(month = today.month + 1, day = 1, hour = 0) # 다음 달 1일로 바꾼 datetime 객체를 넣어준다
            except ValueError: # 한 해의 마지막 달에서 1이 더해진다면 ValueError가 발생하므로 예외 처리
                today = today.replace(year = today.year + 1, month = 1, day = 1, hour = 0) # 다음 년도 1월 1일로 바꾼 datetime 객체를 넣어준다
        return today

    def get_nextMeal(self, today):
        time = [480, 810, 1170] # 각각 아침, 점심, 저녁을 먹는 시간(분 단위로 환산함)
        
        for i in range(len(time)):
            if (today.hour * 60 + today.minute) < time[i]:
                return i
        return len(time)

    def get_info(self, command, keyword = None):
        return getattr(self, "get_%s" % command, "%s 작업을 처리하는데 문제가 발생했습니다." % command)(keyword)

    def get_hungry(self, dump):
        today = self.get_nextDay()
        nextMeal = self.get_nextMeal(today)
        item = ["아침", "점심", "저녁"]

        soup = HTMLGetter("http://www.gsm.hs.kr/xboard/board.php?tbnum=8&sYear=%s&sMonth=%s"
            % (today.year, today.month)).get_soup()

        try:
            info = soup.select("#xb_fm_list > div.calendar > ul > li > div > div.slider_food_list.slider_food%s.cycle-slideshow" % today.day)
            menuList = (info[0].find("div", {"data-cycle-pager-template" : "<a href=#none; class=today_food_on%s title=%s></a>" % (nextMeal % 3 + 1, item[nextMeal % 3])}).find("span", "content").text).split("\n")

            p = re.compile("(?!에너지)[가-힣&\s]+") # 영양성분 문장을 제외하기 위한 정규표현식

            result = ""
            for i in menuList:
                value = p.match(i)
                if value:
                    result +=  ("- "+ value.group() + "\n")

            # result의 길이가 0이면
            if not len(result):
                raise Exception
            return result
        except:
            print("[오류] GSM Bot이 식단표를 받아올 수 없습니다.")
            return "%s 급식을 불러올 수 없습니다." % item[nextMeal % 3]

    def get_calendar(self, dump):
        today = datetime.today()

        soup = HTMLGetter("http://www.gsm.hs.kr/xboard/board.php?tbnum=4").get_soup()

        try:
            info = soup.select("#xb_fm_list > div.calendar > ul > li > dl")
            
            result = "```"
            for i in info:
                if not i.find("dd") == None:
                    text = i.text.replace("\n", "")
                    result += "%6s -%s\n" % (text.split("-")[0], text.split("-")[1])
                    for i in text.split("-")[2:]:
                        result += "%7s -%s\n" % ("", i)
            result += "```"
            return result
        except AttributeError:
            print("[오류] GSM Bot이 학사일정을 불러올 수 없습니다.")
            return "%s년 %s월 학사일정을 불러올 수 없습니다." % (today.year, today.month)

    def get_image(self, keyword):
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

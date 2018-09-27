import requests
from bs4 import BeautifulSoup
import datetime
import random

class crawler:
    def get_html(self, url):
        """
        리턴값 : string
        인자로 받은 url의 HTML 소스를 리턴한다.
        request에 실패한 경우에 NULL이 반환된다.
        """
        response = requests.get(url)
        html = response.text
        return html

    def get_count(self, today):
        """
        리턴값 : string
        0, 1, 2, 3 중 하나를 리턴한다.
        아침을 먹기 전의 시간이라면, 0
        점심을 먹기 전의 시간이라면, 1
        저녁을 먹기 전의 시간이라면, 2
        저녁을 먹고 난 후의 시간이라면, 3
        """
        item = [480, 810, 1170]

        for i in range(len(item)):
            if (today.hour * 60 + today.minute) < item[i]:
                return i
        return 3

    def get_today(self):
        today = datetime.datetime.today()
        index = self.get_count(today) # 아침, 점심, 저녁, 다음 날 아침중에 어떤 식사를 불러와야 하는지를 나타내는 정수
        try:
            today = today.replace(day = int(today.day + index / 3)) # 다음 날 아침을 불러와야 한다면 today에 다음 날로 바꾼 datetime 객체를 넣음
        except ValueError: # 한 달의 마지막 날에서 1이 더해진다면 ValueError가 발생하므로 예외 처리
            try:
                today = today.replace(month = today.month + 1, day = 1) # 다음 달 1일로 바꾼 datetime 객체를 넣어준다
            except ValueError: # 한 해의 마지막 달에서 1이 더해진다면 ValueError가 발생하므로 예외 처리
                today = today.replace(year = today.year + 1, month = 1, day = 1) # 다음 년도 1월 1일로 바꾼 datetime 객체를 넣어준다

        return today

    def get_info(self, link, command):
        """
        리턴값 : string
        command에 따라서 식단표를 출력하거나, 학사 일정을 출력하는 등 처리를 한다.
        """
        html = self.get_html(link)
        soup = BeautifulSoup(html, "html.parser")
        
        return getattr(self, "%s_process" % command, "%s 작업을 처리하는데에 문제가 생겼습니다." % command)(soup)

    def hungry_process(self, soup):
        today = self.get_today()
        index = self.get_count(today)
        item = ["아침", "점심", "저녁"]
        
        try:
            info = soup.select("#xb_fm_list > div.calendar > ul > li > div > div.slider_food_list.slider_food%s.cycle-slideshow" % today.day)
            menuList = (info[0].find("div", {"data-cycle-pager-template" : "<a href=#none; class=today_food_on%s title=%s></a>" % (index % 3 + 1, item[index % 3])}).find("span", "content").text).split("\n")

            for i in range(2): # 탄수화물, 단백질 등의 표시를 제외하고 출력하기 위해 맨 끝에 두 개를 지움
                del menuList[-1]
                
            result = ""
            for i in menuList:
                result +=  "- "+ i.split()[0] + "\n"
                
            return result
    
        except AttributeError:
            print("[Error] GSM Bot can't get a menu")
            return "%s 급식을 불러올 수 없습니다." % item[index]

    def calendar_process(self, soup):
        today = datetime.datetime.today()
        try:
            info = soup.select("#xb_fm_list > div.calendar > ul > li > dl")
            result = "```"

            for i in info:
                if i.find("dd") is not None:
                    text = i.text.replace("\n", "")
                    result += "%6s -%s\n" % (text.split("-")[0], text.split("-")[1])
            result += "```"
            
            return result
            
        except AttributeError:
            print("[Error] GSM Bot can't get a calendar")
            return "%s년 %s월 학사일정을 불러올 수 없습니다." % (today.year, today.month)

    def image_process(self, soup):
        try:
            info = soup.find_all("img")
            index = random.randint(1, len(info)) # 구글 자체 이미지가 포함되어 있기 때문에 1부터 시작한다
            return info[index]["src"] # 이미지의 링크를 가져옴
        except:
            print("[Error] GSM Bot can't get a image")
            return "이미지를 불러올 수 없습니다."

if __name__ == "__main__": # WebCrawler.py를 메인으로 실행할 때만 실행됨
    print(crawler().get_info("https://www.google.co.kr/search?tbm=isch&q=FUCK", "image"))

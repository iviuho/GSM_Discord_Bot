import re
from datetime import date, datetime


class Menu:
    class Time:
        BREAKFAST = "breakfast"
        LUNCH = "lunch"
        DINNER = "dinner"

    def __init__(self, menu_list, today_date):
        """
        Menu 클래스의 생성자

        menu_list: dict
            "breakfast", "lunch", "dinner"이 키로 이루어진 급식 정보 딕셔너리

        today_date: datetime.date
            해당 급식의 날짜 정보
        """
        # 급식의 날짜 정보가 현재 날짜와 일치하는 지 검사
        authenticity = (today_date == date.today())

        self.menu = menu_list
        self.today = menu_list[today_date.day] if authenticity else None
        self.request_time = datetime.now()

    def __str__(self):
        return str(self.menu)

import discord
import asyncio
import datetime
from WebCrawler import crawler
import json
import os
import operator
import re

class GSMBot(discord.Client):
    def __init__(self):
        try:
            with open("admin.json", "r", encoding = "UTF8") as f:
                temp =  json.load(f) # json 파일을 읽어들여서 저장해둠
            self.admin = []
            for i in temp:
                self.admin.append(temp[i]) # Bot 개발자들의 Discord ID를 admin에 추가함
        except FileNotFoundError:
            temp = {"example" : "here_your_discord_id"}
            with open("admin.json", "w", encoding = "UTF8") as f:
                json.dump(temp, f, ensure_ascii = False, indent = 4)
            print("admin.json 파일 생성")

        if not os.path.exists("./keyword"):
            os.makedirs("keyword")
            print("keyword 디렉토리 생성")
        if not os.path.exists("./vote"):
            os.makedirs("vote")
            print("vote 디렉토리 생성")

        self.prefix = "gsm"
        self.color = 0x7ACDF4
        
        self.allCommands = []
        for i in list(filter(lambda param: param.startswith("command_"), dir(self))):
            self.allCommands.append(i)
            
        self.splitCommands = []
        for i in self.allCommands:
            self.splitCommands.append(i.split("command_")[-1])

        self.peekList = []

        super().__init__()
    
    async def on_ready(self):
        await self.change_presence(game = discord.Game(name = "명령어 : GSM"))
        print("GSM Bot Ready!", end = "\n\n")

    async def on_message(self, message):
        await self.wait_until_ready()

        if not message.author.bot: # Bot이 보낸 메시지를 인식하지 않게 하기 위함
            if message.channel.is_private == False:
                await self.message_log(message)
            command = message.content.lower() # 명령어가 대문자로 들어와도 인식할 수 있게 모두 소문자로 변환
            if not command.startswith(self.prefix): # 명령어를 입력한게 아니라면 바로 함수 종료
                return

            command = command.split()[-1] # gsm hi를 입력했다면, 공백을 기준으로 스플릿한 마지막 결과, 즉 hi가 command 변수에 들어가게 됨
            try:
                try: # 디스코드 닉네임이 인식할 수 없는 문자인 경우에 UnicodeEncodeError가 발생하므로 예외처리
                    print("[%02d:%02d] %s : %s" % (datetime.datetime.today().hour, datetime.datetime.today().minute, message.author, command))
                except UnicodeEncodeError:
                    pass
                
                await getattr(self, "command_%s" % command, None)(message)
                # GSMBot 클래스에 해당 명령어가 있으면 message를 넘겨주면서 함수를 실행함
                # 해당 명령어가 존재하지 않는다면 None을 반환한다.
            except TypeError: # None이 반환된다면 TypeError가 발생하므로 예외처리
                print("[Error] %s is not command (User : %s)" % (command, message.author.name))
                return

    async def on_member_update(self, before, after):
        if not before in self.peekList: # 감시 리스트에 있지 않으면 바로 리턴
            return

        msg = None
        em = None

        if not before.status == after.status:
            def temp(status):
                if status == discord.Status.online:
                    return "온라인"
                elif status == discord.Status.offline:
                    return "오프라인"
                elif status == discord.Status.idle:
                    return "자리비움"
                elif status == discord.Status.do_not_disturb:
                    return "다른 용무중"

            msg = "%s님이 %s에서 %s로 상태를 바꿨습니다." % (before.name, temp(before.status), temp(after.status))

        if not before.game == after.game:
            def temp(game):
                if game:
                    return game.name
                else:
                    return "휴식"

            msg = "%s님이 %s을 시작하셨습니다." % (before.name, temp(after.game))

        if not before.avatar == after.avatar:
            def temp(member):
                if member.avatar:
                    return member.avatar_url
                else:
                    return member.default_avatar_url

            em = discord.Embed(title = "%s님이 프로필 사진을 바꾸셨습니다" % before.name)
            em.set_image(temp(after))

        if not before.nick == after.nick:
            def temp(member): # 닉네임이 따로 설정되어 있지 않은 경우에 None이 출력되는 것을 막기 위한 함수
                if member.nick:
                    return member.nick
                else:
                    return member.name

            msg = "%s님이 %s에서 %s로 닉네임을 변경하셨습니다." % (before, temp(before), temp(after))

        for i in before.server.channels: # 채널들을 받아옴
            if i.type == discord.ChannelType.text: # 그 중에 텍스트 채널인 동시에,
                if i.permissions_for(before.server.me).send_messages == True: # 메시지 보내기 권한이 있다면 메시지 출력
                    await self.send_message(i, msg)
                    return # 하나의 채널에만 보내기 위해서 return을 통해 탈출

    async def on_member_remove(self, member):
        for i in member.server.channels:
            if i.type == discord.ChannelType.text:
                if i.permissions_for(member.server.me).send_messages == True:
                    await self.send_message(i, "%s님이 %s에서 탈주하셨습니다." % (member.author.name, member.server.name))
                    return

    async def command_gsm(self, message):
        """
        GSM Bot의 명령어를 모두 출력합니다.
        """
        
        await self.send_typing(message.channel)
        with open("GSMBot.txt", "r", encoding = "UTF8") as f:
            msg = f.read() + "\n"

        allCommands = str()
        for i in self.allCommands: # GSM Bot의 모든 요소를 불러온 후, command_로 시작하는 함수들만 리스트로 만들어서 출력
            allCommands += "***%s***\n" % (i.split("_")[-1]) # command_x에서 _를 기준으로 맨 뒤, 즉 x만 msg에 추가한다
            allCommands += "%s\n" % (getattr(self, i).__doc__).strip()
            
        em = discord.Embed(title = "**GSM Bot**", description = msg, colour = 0x7ACDF4)
        em.add_field(name = "**GSM Bot의 명령어**", value = allCommands)
        em.set_thumbnail(url = "http://www.gsm.hs.kr/data_files/skin/skin_high_gsmhs/images/common/logo.png")
        await self.send_message(message.channel, embed = em)

    async def command_hi(self, message):
        """
        GSM Bot과 인사합니다.
        역시 우리는 사이가 정말 좋습니다.
        """
        
        await self.send_message(message.channel, "%s 안녕!" % message.author.name)

    async def command_logout(self, message):
        """
        GSM Bot을 종료시킵니다.
        Bot의 관리자만 사용 가능합니다.
        """

        if not message.author.id in self.admin: # 이 명령어를 입력한 사용자가 관리자인지 확인
            print("[Error] logout need administer permission. (User : %s)" % message.author.name)
            await self.send_message(message.channel, "GSM Bot을 끌 수 있는건 Bot의 관리자 뿐입니다.")
            return
        
        await self.send_message(message.channel, "GSM Bot이 죽었습니다!")
        await self.logout()

    async def command_hungry(self, message):
        """
        GSM의 다음 식단표를 알려줍니다.
        8:00, 13:30, 19:30을 기준으로 시간이 지나면 표시하는 식단표가 바뀝니다.
        """
        
        await self.send_typing(message.channel)
        today = crawler().get_today() # 오늘의 정보(년도, 월, 일, 시간, 분)이 담겨있는 datetime 객체

        title_ = "%s년 %s월 %s일 %s의 %s 식단표" % (today.year, today.month, today.day,
                ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][int(today.weekday())],
                ["아침", "점심", "저녁"][crawler().get_count(today) % 3])
        em = discord.Embed(title = title_, description = crawler().get_info("http://www.gsm.hs.kr/xboard/board.php?tbnum=8", "hungry"), colour = self.color)
        await self.send_message(message.channel, embed = em)

    async def command_calendar(self, message):
        """
        GSM의 한 달간의 학사일정을 알려줍니다.
        """

        today = datetime.datetime.today()
        title_ = "%s년 %s월의 학사일정" % (today.year, today.month)
        em = discord.Embed(title = title_, description = crawler().get_info("http://www.gsm.hs.kr/xboard/board.php?tbnum=4", "calendar"), colour = self.color)
        await self.send_message(message.channel, embed = em)

    async def command_invite(self, message):
        """
        GSM Bot을 초대하기 위한 링크를 받습니다.
        """

        link = "https://discordapp.com/oauth2/authorize?client_id=489709353536847872&scope=bot&permissions=1"
        em = discord.Embed(title = "☆★☆★GSM Bot 초대 링크★☆★☆", description = "받으세요!", url = link, colour = self.color)
        msg = await self.send_message(message.channel, embed = em)
        await asyncio.sleep(15)
        await self.delete_message(msg)
        await self.send_message(message.channel, "초대 링크는 자동으로 삭제했습니다.")

    async def command_history(self, message):
        """
        해당 서버에서 채팅으로 많이 입력된 키워드들을 보여드립니다.
        1:1 채팅은 이 기능을 지원하지 않습니다.
        """

        if message.channel.is_private: # 채널이 Private이면 바로 그냥 리턴
            await self.send_message(message.channel, "비공개 채팅에서는 지원하지 않습니다. :(")
            return

        title_ = "%s의 입력된 키워드 순위" % message.server.name
        em = discord.Embed(title = title_, colour = self.color)

        with open("./keyword/%s.json" % message.server.id, "r", encoding = "UTF8") as f:
            read = json.load(f)
        
        sortedDict = sorted(read.items(), key = operator.itemgetter(1, 0), reverse = True) # 딕셔너리를 정렬한다. 기준은 value값(입력된 횟수)의 내림차순
        for i in range(0, len(sortedDict)): # sortedDict의 길이만큼 반복하는데
            if i >= 10: # 10위까지만 보여주기 위해서
                break
            em.add_field(name = "%d위" % (i + 1), value = "%s : %d회\n" % (sortedDict[i][0], sortedDict[i][1]))
            
        await self.send_message(message.channel, embed = em)

    async def command_vote(self, message):
        """
        주제를 정하고 OX 찬반 투표를 생성합니다.
        1:1 채팅은 이 기능을 지원하지 않습니다.
        또한 봇에게 메시지 관리 권한이 필요합니다.
        """

        if message.channel.is_private:
            await self.send_message(message.channel, "비공개 채팅에서는 지원하지 않습니다. :(")
            return

        if not message.channel.permissions_for(message.server.get_member(self.user.id)).manage_messages:
            await self.send_message(message.channel, "Bot에게 메시지 관리 권한이 없습니다.")
            return

        channel_id = message.server.id
        directory = "./vote/%s.json" % channel_id

        if os.path.exists(directory): # 파일이 있다면 이미 투표가 진행되고 있다는 의미
            try:
                with open(directory, "r", encoding = "UTF8") as f:
                    data = json.load(f)
            except FileNotFoundError:
                await self.send_message(message.channel, "%s 투표가 종료돼서 제대로 반영이 되지 않았습니다." % message.author.mention)

            em = discord.Embed(title = "현재 %s에 대한 투표가 진행중입니다." % data["subject"], description = "앞에 GSM은 붙이지 않습니다.", colour = self.color)
            em.add_field(name = "찬성 투표", value = "O 입력")
            em.add_field(name = "반대 투표", value = "X 입력")
            
            quest = await self.send_message(message.channel, embed = em)

            response = await self.wait_for_message(timeout = float(10), author = message.author, channel = message.channel)
            # 명령어를 입력한 사용자로부터 답변을 기다린 후, response에 저장해둠
            await self.delete_message(quest) # 질문할 때 보낸 메시지를 지움

            if response == None: # 질문에 대해 시간 초과가 일어나면 None이 리턴된다
                await self.send_message(message.channel, "%s 투표가 제대로 되지 않았습니다. 다시 시도해주세요." % message.author.mention)
                return

            content = response.content

            if content.upper() == "O" or content.upper() == "X": # O나 X로 들어온 답변만 json파일에 입력함
                await self.delete_message(response) # 익명 투표를 위해 답변 메시지도 지움

                data.update({response.author.id : content.upper()}) # 파일을 읽고 받아온 딕셔너리를 업데이트한다

                if os.path.exists(directory): # 투표를 하려고 명령어를 친 후에 투표가 끝나는 경우를 위해서 파일 재검사
                    with open(directory, "w", encoding = "UTF8") as f:
                        json.dump(data, f, ensure_ascii = False, indent = 4)
                else: # 파일이 없다면 투표가 끝났다는 의미이므로 함수 종료
                    await self.send_message(message.channel, "%s 투표가 종료돼서 제대로 반영이 되지 않았습니다." % message.author.mention)
                    return

                await self.send_message(message.channel, "%s의 투표가 잘 처리되었습니다." % response.author.name)
            else:
                await self.send_message(message.channel, "%s 투표가 제대로 처리되지 않았습니다." % response.author.mention)

        else: # 투표가 진행되고 있지 않을 때
            msg = '투표 주제와 투표 시간을 입력해주세요.\n"10분동안 설문" 이라는 제목으로 10분동안 투표하려면\nex) "10분동안 설문 10" 라고 입력해주세요. 앞에 GSM 은 붙이지 않습니다.'
            quest = await self.send_message(message.channel, msg)

            response = await self.wait_for_message(timeout = float(30), author = message.author, channel = message.channel)
            await self.delete_message(quest)

            if response == None:
                await self.send_message(message.channel, "%s 투표가 제대로 시작되지 않았습니다." % message.author.mention)
                return

            content = response.content

            if content.split()[0].lower() == "cancel": # Cancel을 입력했다면 함수를 종료하며 투표 생성 취소
                await self.send_message(message.channel, "투표가 취소되었습니다.")

            try:
                time = float(content.split()[-1]) # 몇 분동안 투표를 진행할건지 파악하기 위해서 스플릿 마지막 결과 저장
            except ValueError: # 문자열을 숫자로 바꾸려고 하면 ValueError 발생
                await self.send_message(message.channel, "투표 시간이 제대로 입력되지 않았습니다.")
                return

            content = content.split()[0:-1] # 스플릿 마지막 결과(시간)을 제외한 나머지를 content에 저장
            subject = str() 
            for i in content: # 입력받았을 때 처럼 띄어쓰기를 넣기 위함
                subject += (i + " ")

            temp = {"subject" : subject} # 딕셔너리에 subject를 저장함
            with open(directory, "w", encoding = "UTF8") as f:
                json.dump(temp, f, ensure_ascii = False, indent = 4) # temp 딕셔너리를 넣은 json파일 생성

            em = discord.Embed(title = "☆★%s의 투표★☆" % message.server.name, colour = self.color)
            em.add_field(name = "%s" % subject, value = "gsm vote를 입력하시고 투표에 참가해주세요!")
            
            await self.send_message(message.channel, embed = em)
            await asyncio.sleep(time * 60) # time을 분 단위로 받았지만 asyncio.sleep은 초 단위로 작동하므로 60을 곱해줌
            
            with open(directory, "r", encoding = "UTF8") as f:
                data = json.load(f) # asyncio.sleep을 통해 대기하는 동안 추가된 데이터를 다시 읽어들임

            del(data["subject"]) # 투표 주제를 제외한
            result = {"O" : 0, "X" : 0} # 나머지 키:값쌍의 value값(O, X)을 저장함
            for i in data:
                result[data[i]] += 1 # result 딕셔너리에 저장함

            em = discord.Embed(title = "☆★%s의 투표결과★☆" % subject, colour = self.color)
            em.add_field(name = "찬성", value = result["O"])
            em.add_field(name = "반대", value = result["X"])
            
            await self.send_message(message.channel, embed = em)

            try:
                os.remove(directory) # 투표가 끝났으므로 파일 삭제
            except PermissionError: # 파일을 프로그램이 점유하고 있을 때 PermissionError 발생
                for i in range(10): # 대략 10초동안 1초마다 삭제를 시도
                    await asyncio.sleep(1)
                    os.remove(directory)

    async def command_image(self, message):
        """
        구글에서 해당 키워드를 검색한 후,
        결과를 사진으로 보내줍니다.
        """

        quest = await self.send_message(message.channel, "검색어를 입력해주세요. 앞에 GSM은 붙이지 않습니다.\n취소하시려면 Cancel을 입력해주세요.")
        response = await self.wait_for_message(timeout = float(15), author = message.author, channel = message.channel)

        await self.delete_message(quest)

        if response == None or response.content.lower() == "cancel":
            await self.send_message(message.channel, "이미지 검색이 취소되었습니다.")
            return

        await self.send_typing(message.channel)

        keyword = response.content
        print("%s : image %s" % (message.author, keyword))
        image = crawler().get_info("https://www.google.co.kr/search?tbm=isch&q=%s" % keyword, "image")
        
        em = discord.Embed(title = "%s의 이미지 검색 결과" % keyword, colour = self.color)
        avatar = message.author.default_avatar_url if message.author.avatar_url == "" else message.author.avatar_url
        # 프로필 사진을 따로 지정해두지 않은 경우에 비어있는 문자열이 반환되므로 이 때는 기본 프로필 사진을 넣어줌
        em.set_footer(text = "%s님이 요청하신 검색 결과" % message.author.name, icon_url = avatar)
        em.set_image(url = image)

        await self.send_message(message.channel, embed = em)

    async def command_peek(self, message):
        """
        GSM Bot의 종료 전까지 선택한 사용자의 상태를 계속해서 감시합니다!
        같은 사용자를 다시 입력할 시엔 감시가 해제됩니다.
        1:1 채팅은 이 기능을 지원하지 않습니다.
        """

        if message.channel.is_private:
            await self.send_message(message.channel, "비공개 채팅에서는 지원하지 않습니다. :(")
            return

        quest = await self.send_message(message.channel, "감시할 사용자를 언급해주세요. 앞에 GSM은 붙이지 않습니다.\n취소하시려면 Cancel을 입력해주세요.")
        response = await self.wait_for_message(timeout = float(15), author = message.author, channel = message.channel)

        await self.delete_message(quest)

        if response == None or response.content.lower() == "cancel":
            await self.send_message(message.channel, "감시가 취소되었습니다.")
            return

        standard = re.compile("<@!?(?P<value>\d+)>") # <@Discord_ID> 나 <@!Discord_ID>에서 Discord_ID만 빼오기 위해 value라는 이름으로 그룹을 지정함
        user = response.content
        result = standard.match(user) # standard 정규 표현식에 만족하는지 검사

        if result: # 조건에 만족한다면
            user = message.server.get_member(result.group("value")) # value로 이름붙인 그룹을 가져와서 discord.Member 객체를 얻음
        else:
            await self.send_message(message.channel, "올바르지 않은 ID 값이 들어왔습니다.")
            return

        if not user in self.peekList:
            self.peekList.append(user)
            await self.send_message(message.channel, "%s의 감시를 시작합니다!" % user.name)
        else:
            self.peekList.remove(user)
            await self.send_message(message.channel, "%s의 감시를 해제합니다." % user.name)

        peekNameList = str()
        for i in self.peekList:
            peekNameList += str(i)
        print("현재 감시 명단 : %s" % peekNameList)

    async def message_log(self, message):
        channel_id = message.server.id # 해당 서버의 고유 아이디
        directory = "./keyword/%s.json" % channel_id # 서버마다 json파일을 생성
        
        if os.path.exists(directory): # 파일이 이미 존재한다면
            with open(directory, "r", encoding = "UTF8") as f: 
                temp = json.load(f) # 파일을 딕셔너리로 읽어온다
        else: # 파일이 없다면
            temp = {} # 비어있는 딕셔너리 생성

        for i in message.content.split():
            if i in self.splitCommands: # 명령어는 키워드로 카운트하지 않기 위해서 제외함
                continue
            value = (lambda b: temp[i] + 1 if b else 1)(i in temp.keys()) # 키워드가 이미 있는지 없는지 검사해서, 있다면 기존 값 + 1 리턴, 없다면 1 리턴
            temp.update({i : value}) # temp 딕셔너리를 업데이트한다. 값이 이미 있다면 값을 바꾸고, 없다면 새로 키:값 쌍을 추가한다

        with open(directory, "w", encoding = "UTF8") as f: # 파일을 쓰기 모드로 열어서
            json.dump(temp, f, ensure_ascii = False, indent = 4) # 새로운 값으로 덮어쓰기한다

birth = datetime.datetime.today()
print("%02d:%02d에 GSM Bot이 태어났습니다." % (birth.hour, birth.minute))

GSMBot().run("NDg5NzA5MzUzNTM2ODQ3ODcy.DoW9QA.DWgVolFc8Jz19_8dQZNC_o_AOpQ")

dead = datetime.datetime.today()
print("\n%02d:%02d에 GSM Bot이 죽었습니다." % (dead.hour, dead.minute))
delta = dead - birth
print("총 켜진 시간 : %02d:%02d:%02d" % (delta.seconds / 3600, (delta.seconds / 60) % 60, delta.seconds % 60))

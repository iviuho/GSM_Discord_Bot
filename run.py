from bot import GSMBot, Timer

TOKEN = "HERE_YOUR_BOTS_TOKEN"
timer = Timer()

timer.start()
GSMBot().run(TOKEN)
hour, minute, second = timer.end()

print("Run Time : %02d:%02d:%02d" % (hour, minute, second))
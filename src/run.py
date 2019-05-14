import configparser
from os.path import dirname, exists, join

from bot import GSMBot, Timer

CONFIG_FILE = join("..", "config", "config.ini")

if exists(CONFIG_FILE):
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
else:
    raise FileNotFoundError("%s doesn't exists" % CONFIG_FILE)

admin = parser.getint("Default", "admin")
token = parser.get("Default", "token")

timer = Timer()

timer.start()
GSMBot(admin=admin).run(token)
hour, minute, second = timer.end()

print("Run Time : %02d:%02d:%02d" % (hour, minute, second))
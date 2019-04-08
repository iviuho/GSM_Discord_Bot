from bot import GSMBot, runtime_calc

# TOKEN = "HERE_YOUR_BOTS_TOKEN"
TOKEN = "NDg5NzA5MzUzNTM2ODQ3ODcy.D3DLww.R_0IFgHAktXs2pH_mkTMOSnrv7E"
timer = runtime_calc()

next(timer)
GSMBot().run(TOKEN)
runtime = next(timer)

print("Run Time : %02d:%02d:%02d" % (runtime / 3600, (runtime / 60) % 60, runtime % 60))
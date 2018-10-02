import subprocess
import os

class Downloader:
    def __init__(self):
        self.path = os.getcwd().replace("\\", "/")
        self.youtube_dl = self.path + "/bin/youtube-dl.exe"
        self.ffmpeg = self.path + "/bin/ffmpeg.exe"
        self.ffprobe = self.path + "/bin/ffprobe.exe"

        self.log = ""
        self.fileName = ""

        if not os.path.exists(self.youtube_dl):
            print(self.youtube_dl + " 파일이 존재하지 않습니다.")
            print("https://youtube-dl.org/downloads/latest/youtube-dl.exe 에서 다운받으세요.")

        if not os.path.exists(self.ffmpeg):
            print(self.ffmpeg + " 파일이 존재하지 않습니다.")
            print("https://ffmpeg.zeranoe.com/builds/ 에서 다운받으세요.")

        if not os.path.exists(self.ffprobe):
            print(self.ffprobe + " 파일이 존재하지 않습니다.")
            print("https://ffmpeg.zeranoe.com/builds/ 에서 다운받으세요.")

    def download_music(self, url):
        try:
            self.log = subprocess.check_output("\"" + self.youtube_dl + "\" -x --audio-format mp3 --audio-quality 0 " + url, shell = True).decode("cp949").replace("\r", "")
        except subprocess.CalledProcessError:
            self.log = ""

        def set_fileName(): # 파일 이름을 받아서 리턴하는 함수
            if self.log == "":
                return None
            
            for i in self.log.split("\n"):
                if i.startswith("[ffmpeg] Destination: "):
                    return i.split("[ffmpeg] Destination: ")[-1]

        self.fileName = set_fileName() # self.fileName에 파일 이름을 받아옴

    def get_version(self):
        return subprocess.check_output(self.youtube_dl + " --version").decode("cp949")

    def get_fileName(self):
        return self.fileName

if __name__ == "__main__":
    pass

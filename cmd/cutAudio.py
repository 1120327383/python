from pydub import AudioSegment
import os


def slice_file(base, file, skip):
    audio = AudioSegment.from_mp3(os.path.join(base, file))
    audio[skip * 1000:].export("F:/projects/myprojects/xdemo/apps/utils/Testings/mp3_new/" + file, format="mp3")


if __name__ == '__main__':
    base = "F:/projects/myprojects/xdemo/apps/utils/Testings/mp3"
    for each in os.listdir(base):
        print(each)
        slice_file(base, each, 35)

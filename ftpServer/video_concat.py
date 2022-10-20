from moviepy.editor import *

c1 = VideoFileClip("raw20220928-1550.mp4")
c2 = VideoFileClip("raw20220928-1650.mp4")
c3 = VideoFileClip("raw20220928-1750.mp4")
c4 = VideoFileClip("raw20220928-1850.mp4")
c5 = VideoFileClip("raw20220928-1950.mp4")
c6 = VideoFileClip("raw20220928-2050.mp4")
#c7 = VideoFileClip("raw20220928-2150.mp4")

hour6v = [c1, c2, c3, c4, c5, c6]

day1v = hour6v + hour6v + hour6v

day3v = day1v + day1v + day1v

final = concatenate_videoclips(day3v)

final.write_videofile("conc220928-15-20-3d.mp4")

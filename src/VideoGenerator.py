import os
from math import floor
#import numpy, cv2
from subprocess import Popen, PIPE, DEVNULL, STDOUT
from .Controller import Controller
from .Inputs import Inputs
from .CONFIG import *

class VideoGenerator:

    def __init__(self, layout, ghost_file):
        self.internal_frame_rate = 59.94
        self.controller = Controller()

        self.controller.read_json(layout)
        self.inputs = Inputs()
        self.inputs.read_file(ghost_file)

    def run(self):
        #video = cv2.VideoWriter(f"demp.{VIDEO_EXTENSION}", cv2.VideoWriter_fourcc(*VIDEO_CODEC), VIDEO_FRAME_RATE, self.controller.size)
        p = Popen(["ffmpeg", "-y", "-f", "image2pipe", "-framerate", str(VIDEO_FRAME_RATE), "-i", "-",
        "-vcodec", "png", "-framerate", str(VIDEO_FRAME_RATE), f"video.{VIDEO_EXTENSION}"],
        stdin=PIPE, stdout=DEVNULL, stderr=STDOUT)

        frame_f = 0.0
        total_frames = self.inputs.get_total_frame_nr()
        while frame_f < total_frames:
            frame = floor(frame_f)
            cur_inputs = self.inputs.get_frame(frame)
            self.controller.process_inputs_and_draw(cur_inputs, TRANSPARENT)
            #video.write(cv2.cvtColor(numpy.array(self.controller.canvas.canvas), cv2.COLOR_RGB2BGR))
            self.controller.canvas.write_to_file(p.stdin, "png")

            percentage = floor(frame * 100 / total_frames)
            print(f"FRAMES WRITTEN : {percentage}% {floor(percentage/5) * '█'}{floor((100-percentage)/5) * '░'}", end="\r")

            frame_f += self.internal_frame_rate / VIDEO_FRAME_RATE

        #video.release()

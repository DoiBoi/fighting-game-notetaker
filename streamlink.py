import subprocess
import cv2
import numpy as np

class Stream:
    def __init__(self,
                 channel="https://www.twitch.tv/tampaneversleeps",
                 streamlink_cmd=None,
                 ffmpeg_cmd=None,
                 width=1280,
                 height=720) -> None:
        self.channel = channel
        self.streamlink_cmd = streamlink_cmd or [
                "streamlink", channel, "best",
                "--stdout", "--quiet"
            ]
        self.ffmpeg_cmd = ffmpeg_cmd or [
            "ffmpeg",
            "-i", "pipe:0",
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-vf", f"scale={width}:{height}",
            "-r", "60",             
            "pipe:1"
        ]
        self.width = width
        self.height = height
        self.streamlink_proc = None
        self.ffmpeg_proc = None

    def start(self):
        self.streamlink_proc = subprocess.Popen(self.streamlink_cmd, stdout=subprocess.PIPE)
        self.ffmpeg_proc = subprocess.Popen(
            self.ffmpeg_cmd,
            stdin=self.streamlink_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )   

    def run(self):
        frame_size = self.width * self.height * 3

        try:
            if self.streamlink_proc is None or self.ffmpeg_proc is None:
                self.start()

            if self.ffmpeg_proc is None or self.ffmpeg_proc.stdout is None:
                return

            while True:
                raw = self.ffmpeg_proc.stdout.read(frame_size)
                if len(raw) < frame_size:
                    break

                frame = np.frombuffer(raw, dtype=np.uint8).reshape((self.height, self.width, 3))
                cv2.imshow("Stream", frame)

                if cv2.waitKey(8) & 0xFF == ord("q"):
                    break
        finally:
            self.cleanup()

    def cleanup(self):
        cv2.destroyAllWindows()

        if self.streamlink_proc is not None:
            self.streamlink_proc.terminate()
        if self.ffmpeg_proc is not None:
            self.ffmpeg_proc.terminate()


if __name__ == "__main__":
    stream = Stream()
    stream.run()


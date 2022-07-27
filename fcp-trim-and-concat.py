import subprocess

output_file = "out.mp4"

# timecode_list = ['00\:00\:08.400', '00\:37\:49.767', '00\:37\:56.733', '00\:45\:28.167']

filter_complex_command = """
                        [0:v]trim=start='00\:00\:08.400':end='00\:01\:49.767', setpts=PTS-STARTPTS, format=yuv420p[0v];
                        [0:1]atrim=start='00\:00\:08.400':end='00\:01\:49.767', asetpts=PTS-STARTPTS[0audio_left];
                        [0:2]atrim=start='00\:00\:08.400':end='00\:01\:49.767', asetpts=PTS-STARTPTS[0audio_right];
                        [0audio_left][0audio_right]amerge=inputs=2 [0audio_merged];
                        [0:v]trim=start='00\:03\:59.000':end='00\:04\:28.167', setpts=PTS-STARTPTS, format=yuv420p[1v];
                        [0:1]atrim=start='00\:03\:59.000':end='00\:04\:28.167', asetpts=PTS-STARTPTS[1audio_left];
                        [0:2]atrim=start='00\:03\:59.000':end='00\:04\:28.167', asetpts=PTS-STARTPTS[1audio_right];
                        [1audio_left][1audio_right]amerge=inputs=2 [1audio_merged];
                        [0v][0audio_merged][1v][1audio_merged]concat=n=2:v=1:a=1[outv][outa]
                        """

def run_FFmpeg(input_file):
    subprocess.run(['ffmpeg', "-i", input_file, "-filter_complex", filter_complex_command, "-map", "[outv]", "-map", "[outa]", "-y", output_file])

def main():
    input_file = input("Enter file path: ")
    run_FFmpeg(input_file)

if __name__ == "__main__":
    main()
import subprocess
import json

output_file = "out.mp4"

timecode_list = ['00\:00\:08.400', '00\:37\:49.767', '00\:37\:56.733', '00\:45\:28.167']

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

example_dict = {
    1:1,
    2:2
}

def build_trim_string(stream_index, in_point, end_point, clip_number, video_clip=True):
    a_check = None if video_clip else 'a'
    format_check = 'format=yuv420p' if video_clip else None
    trim_string = f"""
    [0:{stream_index}]{a_check}trim=start='{in_point}':end='{end_point},
    {a_check}setpts=PTS-STARTPTS,{format_check}[clip_{clip_number}_video_stream_{stream_index}]'
    """ 
    return trim_string

def build_ffmpeg_filter(stream_info, timecode_list):
    ffmpeg_filter_string = ""

# def format_video_trim_string(stream_index, in_point, end_point, clip_number):
#     video_trim_string = f"[0:{stream_index}]trim=start='{in_point}':end='{end_point}', setpts=PTS-STARTPTS, format=yuv420p[clip_{clip_number}_video_stream_{stream_index}]"
#     return video_trim_string

# def format_audio_trim_string(stream_index, in_point, end_point, clip_number):
#     audio_trim_string = f"[0:{stream_index}]atrim=start='{in_point}':end='{end_point}', asetpts=PTS-STARTPTS[clip_{clip_number}_audio_stream_{stream_index}]"
#     return audio_trim_string  

def merge_audio_streams(audio_input_list, clip_number):

    merged_stream = f"[0audio_left][0audio_right]amerge=inputs={len(audio_input_list)} [{clip_number}audio_merged];"


def get_stream_info_json(input_file):
    stream_info_string = subprocess.run(
        ['ffprobe',
        '-loglevel',
        'error',
        '-show_entries',
        'stream=index,codec_type',
        '-of', 'json',
        input_file],
        capture_output=True
        ).stdout

    return json.loads(stream_info_string)

def run_ffmpeg(input_file):
    subprocess.run(['ffmpeg', "-i", input_file, "-filter_complex", filter_complex_command, "-map", "[outv]", "-map", "[outa]", "-y", output_file])

def main():
    input_file = input("Enter file path: ")
    stream_info_dict = get_stream_info_json(input_file)
    build_ffmpeg_filter(stream_info_dict, timecode_list)
    # print(stream_info_dict)
    # run_ffmpeg(input_file)

if __name__ == "__main__":
    main()
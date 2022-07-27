import subprocess
import json
import time

output_file = "out.mp4"

timecode_list = [('00\:00\:08.400', '00\:37\:49.767'), ('00\:37\:56.733', '00\:45\:28.167')]

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

def iteration_test(timecode_list, stream_info, merge_audio=True):

    for clip_number, timecode_pair in enumerate(timecode_list):
        current_stream_index = 0
        audio_stream_list = []
        in_point = timecode_pair[0]
        out_point = timecode_pair[1]

        while current_stream_index < len(stream_info):
            codec_type = stream_info[current_stream_index]['codec_type']
            trim_string = build_trim_string(current_stream_index, in_point, out_point, clip_number, codec_type)
            print(trim_string)
            if codec_type == 'audio':
                audio_stream_list.append(f"[clip_{clip_number}_{codec_type}_stream_{current_stream_index}]")
            
            current_stream_index += 1

        if len(audio_stream_list) > 1:
            audio_merge_string = build_audio_merge_string(audio_stream_list, clip_number)
            print(audio_merge_string)


def build_trim_string(stream_index, in_point, out_point, clip_number, codec_type):
    a_check = 'a' if codec_type == 'audio' else ''
    format_check = ',format=yuv420p' if codec_type == 'video' else ''
    trim_string = f"""
    [0:{stream_index}]{a_check}trim=start='{in_point}':end='{out_point},
    {a_check}setpts=PTS-STARTPTS
    {format_check}[clip_{clip_number}_{codec_type}_stream_{stream_index}]
    """ 
    return trim_string

def build_audio_merge_string(audio_stream_list, clip_number):
    audio_merge_string = ""

    for audio_stream in audio_stream_list:
        audio_merge_string += audio_stream
    
    audio_merge_string += f"amerge=inputs={len(audio_stream_list)} [{clip_number}_audio_merged]"

    return audio_merge_string


def build_ffmpeg_filter(stream_info, timecode_list):
    ffmpeg_filter_string = ""

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
    iteration_test(timecode_list, stream_info_dict['streams'])
    # build_ffmpeg_filter(stream_info_dict, timecode_list)
    # print(stream_info_dict)
    # run_ffmpeg(input_file)

if __name__ == "__main__":
    main()
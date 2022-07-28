import subprocess
import json
from collections import namedtuple

output_file = "out.mp4"

TimecodePair = namedtuple("TimecodePair", "in_point out_point")
Filter = namedtuple("Filter", "arguments label")

timecode_list = [TimecodePair('00\:00\:08.400', '00\:37\:49.767'), TimecodePair('00\:37\:56.733', '00\:45\:28.167')]

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

def build_ffmpeg_filter(timecode_list, stream_info, merge_audio=True):

    filter_commands_list = []
    concat_filter_string = ""

    for clip_number, timecode in enumerate(timecode_list):
        current_stream_index = 0
        audio_merge_list = []

        while current_stream_index < len(stream_info):
            codec_type = stream_info[current_stream_index]['codec_type']
            trim_string = build_trim_string(current_stream_index, timecode.in_point, timecode.out_point, codec_type)
            label_string = build_label_string(clip_number, codec_type, current_stream_index)
            filter_command = Filter(trim_string, label_string)
            filter_commands_list.append(filter_command)
            
            if (codec_type == 'audio') and (merge_audio):
                audio_merge_list.append(filter_command.label)
            elif (codec_type == 'audio') or (codec_type == 'video'):
                concat_filter_string += filter_command.label

            current_stream_index += 1

        if merge_audio:
            audio_merge_filter = build_audio_merge_filter(audio_merge_list, clip_number)
            filter_commands_list.append(''.join(audio_merge_filter))
            concat_filter_string += audio_merge_filter.label

    concat_filter_string += f"concat=n={len(timecode_list)}:v=1:a=1[outv][outa]"
    filter_commands_list.append(concat_filter_string)

    return filter_commands_list

def build_trim_string(stream_index, in_point, out_point, codec_type):
    a_check = 'a' if codec_type == 'audio' else ''
    format_check = ',format=yuv420p' if codec_type == 'video' else ''
    trim_string = f"""
    [0:{stream_index}]{a_check}trim=start='{in_point}':end='{out_point},
    {a_check}setpts=PTS-STARTPTS
    {format_check}
    """ 
    return trim_string

def build_label_string(clip_number, codec_type, stream_index):
    return f"[clip_{clip_number}_{codec_type}_stream_{stream_index}]"

def build_audio_merge_filter(audio_merge_list, clip_number):
    arguments = f'{"".join(audio_merge_list)}amerge=inputs={len(audio_merge_list)}'
    label = f'[clip_{clip_number}_audio_merged]'
    return Filter(arguments, label)

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
    build_ffmpeg_filter(timecode_list, stream_info_dict['streams'])
    # run_ffmpeg(input_file)

if __name__ == "__main__":
    main()
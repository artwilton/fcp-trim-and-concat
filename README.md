# fcp-trim-and-concat
Trim and concatenate videos files using Final Cut Pro and FFmpeg.

**This script is currently still in progress,** but should work fine in most scenarios where stream 0 is the primary video stream and there is at least one audio stream.

### Notes:

For the time being / proof of concept stage, the timecode values need to be hardcoded into the `timecode_list` variable, which contains a list of named tuples, representing each timecode range to keep. These timecode values are inclusive, and everything not included in a timecode range will be trimmed from the final output file.

### Next steps:

- Integrate with FCPX Marker Tool, allowing for a marker list to be used as input for timecode ranges
- Add argument parsing to allow user to pass in input, output, ffmpeg settings, etc.
- Add checks for file input and output validity


### Issues I've encountered while working on this script:

While working with older .mov video files captured from a Hi-8 camera as DV/NTSC, I noticed that certain files had multiplexing errors in the video stream, causing certain frames to be repeated. The way Final Cut Pro handled this was slightly different than FFmpeg, so in order for the trimming to be accurate when using FCP to set markers, I had to re-mux the original video file with FFMpeg using the following syntax `ffmpeg -i <INPUT> -c copy -map -0 <OUTPUT>.mov` and then re-import into FCP before setting any markers.This script is currently still in progress, but should work fine in most scenarios where stream 0 is the primary video stream and there is at least.
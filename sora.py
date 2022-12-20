import io
import struct
import os
import argparse

parser = argparse.ArgumentParser(description="UbiArt audio maker for Wii games")

parser.add_argument("-i", "--input", help="Input audio", required=True)
parser.add_argument("-o", "--output", help="Output audio")
parser.add_argument("-f", "--ffmpeg-executable-path", default="ffmpeg.exe", help="Path to FFmpeg")
parser.add_argument("-v", "--vgaudiocli-executable-path", default="vgaudiocli.exe", help="Path to VGAudioCLI")
parser.add_argument("-s", "--split-channels", action="store_true", help="Split audio channels (this is needed only for sounds)")


# Function what builds not-interleaved stereo audio
def build_lr_audio():
    header_buf = io.BytesIO()
    dsp_headers_buf = io.BytesIO()

    # Writing the header stuff
    header_buf.write(b"\0\0\x01\x2E\0\0\x01\x40\0\0\0\x05\0\0\0\0\x66\x6D\x74\x20\0\0\0\x5C\0\0\0\x12\x64\x73\x70\x4C\0\0\0\x6E\0\0\0\x60\x64\x73\x70\x52\0\0\0\xCE\0\0\0\x60")
    header_buf.write(b"\x64\x61\x74\x4C\0\0\x01\x40") # datL

    left_buf = io.BytesIO()
    right_buf = io.BytesIO()

    with open("temp/left.dsp", "rb") as left:
        # Reading and writing the left .DSP header
        left_header = left.read(0x60)
        dsp_headers_buf.write(left_header)

        # Reading and writing the left data
        left_data = left.read()
        left_buf.write(left_data)

        with open("temp/right.dsp", "rb") as right:
            # Reading and writing the right .DSP header
            right_header = right.read(0x60)
            dsp_headers_buf.write(right_header)

            # Reading and writing the right data
            right_data = right.read()
            right_buf.write(right_data)

            # Getting the left and right channel data size
            left_size = left_buf.tell()
            right_size = right_buf.tell()

            # Writing the header stuff
            header_buf.write(struct.pack(">I", left_size))

            header_buf.write(b"datR")
            header_buf.write(struct.pack(">II", 0x140 + left_size, right_size))

    # Writing the padding 
    dsp_headers_buf.write(b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0")
    return header_buf.getvalue(), dsp_headers_buf.getvalue(), left_buf.getvalue() + right_buf.getvalue()


# Function what builds interleaved stereo audio
def build_mixed_audio():
    header_buf = io.BytesIO()
    dsp_headers_buf = io.BytesIO()

    # Writing the header stuff
    header_buf.write(b"\0\0\x01\x22\0\0\x01\x40\0\0\0\x04\0\0\0\x03\x66\x6D\x74\x20\0\0\0\x50\0\0\0\x12\x64\x73\x70\x4C\0\0\0\x62\0\0\0\x60\x64\x73\x70\x52\0\0\0\xC2\0\0\0\x60")
    header_buf.write(b"\x64\x61\x74\x53\0\0\x01\x40") # datS
    
    stereo_buf = io.BytesIO()

    with open("temp/left.dsp", "rb") as left:
        # Reading and writing the left .DSP header
        left_header = left.read(0x60)
        dsp_headers_buf.write(left_header)

        with open("temp/right.dsp", "rb") as right:
            # Reading and writing the right .DSP header
            right_header = right.read(0x60)
            dsp_headers_buf.write(right_header)

            left.seek(0, os.SEEK_END)

            # Getting the data size and writing nibble count
            data_size = left.tell() - 0x60
            header_buf.write(left_header[4:8])

            left.seek(0x60, os.SEEK_SET)

            # Reading and writing the left & right data
            pointer = 0
            while pointer < data_size:
                left_data = left.read(0x8)
                right_data = right.read(0x8)

                stereo_buf.write(left_data + right_data)

                pointer += 8

    return header_buf.getvalue(), dsp_headers_buf.getvalue(), stereo_buf.getvalue()


# Main function
def main():
    # Parsing the command line-arguments
    args = parser.parse_args()

    # Creating the temporary directory if we can do it
    if not os.path.exists("temp"):
        os.mkdir("temp")

    output_file = args.output if args.output else os.path.splitext(args.input)[0] + ".wav.ckd"

    # Converting the input audio to left/right mono .WAV files
    os.system(f"{args.ffmpeg_executable_path} -i {args.input} -filter_complex \"[0:a]aformat=sample_fmts=s32:sample_rates=32000[audio_32000hz];[audio_32000hz]channelsplit=channel_layout=stereo[l][r]\" -map \"[l]\" temp/left.wav -map \"[r]\" temp/right.wav")

    # Converting the .WAV files to .DSP
    os.system(f"{args.vgaudiocli_executable_path} temp/left.wav temp/left.dsp")
    os.system(f"{args.vgaudiocli_executable_path} temp/right.wav temp/right.dsp")

    if args.split_channels:
        # Building the non-interleaved stereo audio
        header, dsp_headers, audio_data = build_lr_audio()

        # Writing data to the output file
        with open(output_file, "wb") as f:
            f.write(b"\x52\x41\x4B\x49\0\0\0\x09\x57\x69\x69\x20\x61\x64\x70\x63")
            f.write(header + b"\0\x02\0\x02\0\0\x7D\0\0\0\xFA\0\0\x02\0\x10\x0E\0")
            f.write(dsp_headers + audio_data)
    else:
        # Building the interleaved stereo audio
        header, dsp_headers, audio_data = build_mixed_audio()

        # Writing data to the output file
        with open(output_file, "wb") as f:
            f.write(b"\x52\x41\x4B\x49\0\0\0\x09\x57\x69\x69\x20\x61\x64\x70\x63")
            f.write(header + b"\0\x02\0\x02\0\0\x7D\0\0\0\xFA\0\0\x02\0\x10\0\0")
            f.write(dsp_headers)
            
            f.seek(0x120, os.SEEK_SET) # TODO: fix it by normal way
            f.write(audio_data)

    # Removing the .WAV and .DSP files
    os.remove("temp/left.wav")
    os.remove("temp/right.wav")
    os.remove("temp/left.dsp")
    os.remove("temp/right.dsp")

    # Removing the temporary directory if we can do it
    if len(os.listdir("temp")) == 0:
        os.rmdir("temp")


if __name__ == "__main__":
    main()

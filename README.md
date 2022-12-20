<p align="center">
  <img src="https://static.wikia.nocookie.net/dokodemo/images/9/99/Sora.png/revision/latest/scale-to-width-down/256"
       alt="Sora (Doko Demo Issyo series)">
</p>

<h1 align="center">Sora</h1>

UbiArt texture encoder for Wii games.

### Features
- Not-interlaced and interlaced support
- Makes DSP automatically using VGAudioCLI
- Command line interface
- Fast as it possible in Python

### Usage
```
sora.py [-h] -i INPUT [-o OUTPUT] [-f FFMPEG_EXECUTABLE_PATH] [-v VGAUDIOCLI_EXECUTABLE_PATH] [-s]

optional arguments:
  -i INPUT, --input INPUT
                        Input audio
  -o OUTPUT, --output OUTPUT
                        Output audio
  -f FFMPEG_EXECUTABLE_PATH, --ffmpeg-executable-path FFMPEG_EXECUTABLE_PATH
                        Path to FFmpeg
  -v VGAUDIOCLI_EXECUTABLE_PATH, --vgaudiocli-executable-path VGAUDIOCLI_EXECUTABLE_PATH
                        Path to VGAudioCLI
  -s, --split-channels  Split audio channels (this is needed only for sounds)
```

### Contribute!
Any contribution, bug reports and help is welcome here.

Check [issue page](https://github.com/lurkook/sora/issues).

### License
This repository ([lurkook/sora](https://github.com/lurkook/sora)) is licensed under [Apache License 2.0](https://github.com/lurkook/sora/blob/master/LICENSE).

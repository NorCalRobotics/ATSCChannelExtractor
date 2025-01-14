#!/usr/bin/env bash
# Copyright (c) 2025 NorCal Robotics - All Rights Reserved.
#
# This source code is licensed under the MIT License.
#
# You may obtain a copy of the License at
#
#      https://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Gabriel Field

import subprocess
import threading
import shutil
import os


def _avconv_argv(config: dict, video_filename: str, audio_filename: str, schedule_entry: dict):
    s_duration = str(schedule_entry["duration_minutes"] * 62) + "s"
    res = config["resolution"] if "resolution" in config else "1920x1080"
    fps = config["fps"] if "fps" in config else "60"
    bitrate = config["bitrate"] if "bitrate" in config else "8M"
    output_filename = schedule_entry["filename"] if "filename" in schedule_entry else "program.mp4"

    binary = shutil.which("ffmpeg")
    if binary is None:
        binary = shutil.which("avconv")
    if binary is None:
        return None

    return [
        shutil.which("timeout"),
        s_duration,
        binary,
        "-pix_fmt", "uyvy422",
        "-s", res,
        "-ac", "2",
        "-f", "rawvideo",
        "-i", video_filename,
        "-f", "s16le",
        "-i", audio_filename,
        "-c:v", "libx264",
        "-b:v", bitrate,
        "-c:a", "aac",
        "-b:a", "128k",
        "-preset", "ultrafast",
        output_filename
    ]


def _v4l_argv(config: dict, schedule_entry: dict, output_filename: str):
    s_duration = str(schedule_entry["duration_minutes"] * 60)
    res = config["resolution"] if "resolution" in config else "1920x1080"
    v4l_fmt = "width=%s,height=%s,pixelformat=UYVY" % tuple(res.split("x"))

    binary = shutil.which("v4l2-ctl")
    if binary is None:
        return None

    return [
        shutil.which("timeout"),
        s_duration + "s",
        binary,
        "--device=" + config["v4l_dev"],
        "--set-fmt-video=" + v4l_fmt,
        "--stream-mmap",
        "--stream-to=" + output_filename
    ]


def _alsa_argv(config: dict, schedule_entry: dict):
    s_duration = str(schedule_entry["duration_minutes"] * 60)
    if "alsa_card" in config:
        alsa_hwid = "hw:CARD=" + config["alsa_card"] + ",DEV=0"
    else:
        alsa_hwid = "hw:" + (config["snd_ctl_dev"])[-1] + ",DEV=0"

    binary = shutil.which("arecord")
    if binary is None:
        return None

    return [
        binary,
        "-f", "cd",
        "-D", alsa_hwid,
        "-d", s_duration,
        "-t", "raw"
    ]


def v4l2_record_video_only(config: dict, schedule_entry: dict, output_filename=None):
    if output_filename is None:
        output_filename = schedule_entry["filename"] if "filename" in schedule_entry else "capture.yuv"
    v4l_argv = _v4l_argv(config, schedule_entry, output_filename)
    return subprocess.call(v4l_argv)


def alsa_record_audio_only(config: dict, schedule_entry: dict, output_filename=None):
    if output_filename is None:
        output_filename = schedule_entry["filename"] if "filename" in schedule_entry else "capture.wav"
    alsa_argv = _alsa_argv(config, schedule_entry)
    return subprocess.call(alsa_argv, stdout=open(output_filename, "w"))


def combine_audio_video(config: dict, video_filename: str, audio_filename: str, schedule_entry: dict):
    avconv_argv = _avconv_argv(config, video_filename, audio_filename, schedule_entry)
    return subprocess.call(avconv_argv)


def v4l2_record_a_v_sep(config: dict, schedule_entry: dict):
    avconv_argv = _avconv_argv(config, "video_pipe", "audio_pipe", schedule_entry)
    v4l_argv = _v4l_argv(config, schedule_entry, "video_pipe")

    os.mkfifo("video_pipe")
    os.mkfifo("audio_pipe")

    recording_threads = list()
    recording_threads.append(threading.Thread(target=subprocess.call, args=(avconv_argv,)))
    recording_threads.append(threading.Thread(target=subprocess.call, args=(v4l_argv,)))

    for t in recording_threads:
        t.start()

    alsa_record_audio_only(config, schedule_entry, "audio_pipe")

    for t in recording_threads:
        t.join()

    os.remove("video_pipe")
    os.remove("audio_pipe")

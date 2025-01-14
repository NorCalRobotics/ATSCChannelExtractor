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


def v4l2_record_a_v_sep(config: dict, schedule_entry: dict):
    s_duration = str(schedule_entry["duration_minutes"] * 60)
    bitrate = config["bitrate"] if "bitrate" in config else "8M"
    res = config["resolution"] if "resolution" in config else "1920x1080"
    fps = config["fps"] if "fps" in config else "60"
    output_filename = schedule_entry["filename"] if "filename" in schedule_entry else "program.mp4"
    v4l_fmt = "width=%s,height=%s,pixelformat=YUYV" % tuple(res.split("x"))
    if "alsa_card" in config:
        alsa_hwid = "hw:CARD=" + config["alsa_card"] + ",DEV=0"
    else:
        alsa_hwid = "hw:" + (config["snd_ctl_dev"])[-1] + ",DEV=0"

    os.mkfifo("video_pipe")
    os.mkfifo("audio_pipe")

    recording_threads = list()
    recording_threads.append(threading.Thread(target=subprocess.call, args=([
        shutil.which("timeout"),
        str(schedule_entry["duration_minutes"] * 62) + "s",
        shutil.which("avconv"),
        "-pix_fmt", "yuyv422",
        "-s", res,
        "-r", fps,
        "-f", "rawvideo",
        "-i", "video_pipe",
        "-f", "s16le",
        "-i", "audio_pipe",
        "-c:v", "libx264",
        "-b:v", bitrate,
        "-preset", "ultrafast",
        output_filename
    ],)))

    recording_threads.append(threading.Thread(target=subprocess.call, args=([
        shutil.which("timeout"),
        s_duration + "s",
        shutil.which("v4l2-ctl"),
        "--device=" + config["v4l_dev"],
        "--set-fmt-video=" + v4l_fmt,
        "--stream-mmap",
        "--stream-to=video_pipe"
    ],)))

    for t in recording_threads:
        t.start()

    subprocess.call([
        "arecord",
        "-f", "cd",
        "-D", alsa_hwid,
        "-d", s_duration,
        "-t", "raw"
    ], stdout=open("audio_pipe", "w"))

    for t in recording_threads:
        t.join()

    os.remove("video_pipe")
    os.remove("audio_pipe")

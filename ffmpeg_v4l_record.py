#!/usr/bin/env python3
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


def call_ffmpeg_a_v_sep(config: dict, schedule_entry: dict):
    s_duration = str(schedule_entry["duration_minutes"] * 60)
    bitrate = config["bitrate"] if "bitrate" in config else "8M"
    res = config["resolution"] if "resolution" in config else "1920x1080"
    fps = config["fps"] if "fps" in config else "60"
    output_filename = schedule_entry["filename"] if "filename" in schedule_entry else "program.mp4"

    ffmpeg_threads = list()
    ffmpeg_threads.append(threading.Thread(target=subprocess.call, args=([
        shutil.which("ffmpeg"),
        "-thread_queue_size", "32",
        "-f", "alsa",
        "-i", config["snd_dev"],
        "-t", s_duration,
        "temp.mp3"
    ],)))

    ffmpeg_threads.append(threading.Thread(target=subprocess.call, args=([
        shutil.which("ffmpeg"),
        "-thread_queue_size", "32",
        "-s", res,  # RESOLUTION
        "-r", fps,  # FRAME_RATE
        "-f", "v4l2",
        "-i", config["v4l_dev"],
        "-b:v", bitrate,
        "-t", s_duration,
        "temp.mp4"
    ],)))

    for t in ffmpeg_threads:
        t.start()

    for t in ffmpeg_threads:
        t.join()

    return subprocess.call([
        shutil.which("ffmpeg"),
        "-i", "temp.mp3",
        "-i", "temp.mp4",
        "-b:v", bitrate,  # BITRATE
        "-vsync", "1",
        output_filename
    ])


def call_ffmpeg(config: dict, schedule_entry: dict):
    s_duration = str(schedule_entry["duration_minutes"] * 60)
    bitrate = config["bitrate"] if "bitrate" in config else "8M"
    res = config["resolution"] if "resolution" in config else "1920x1080"
    fps = config["fps"] if "fps" in config else "60"
    output_filename = schedule_entry["filename"] if "filename" in schedule_entry else "program.mp4"

    ffmpeg_argv = [
        shutil.which("ffmpeg"), "-thread_queue_size", "32",
        "-f", "alsa",
        "-i", config["snd_dev"],
        "-f", "v4l2",
        "-i", config["v4l_dev"],
        "-t", s_duration,
        "-s", res,  # RESOLUTION
        "-r", fps,  # FRAME_RATE
        "-b:v", bitrate,  # BITRATE
        "-vsync", "1",
        output_filename
    ]

    return subprocess.call(ffmpeg_argv)
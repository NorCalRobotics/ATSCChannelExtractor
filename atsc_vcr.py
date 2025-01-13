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

import datetime
import pytz
import time
import json
import glob
import os
from atsc_channels import get_atsc_channel
from adaptor_tuning import mux_pids, select_frequency, set_mux_pids
from ffmpeg_v4l_record import call_ffmpeg


def start_recording(config: dict, schedule_entry: dict):
    info_fmt = "Starting recording on channel %s for %d minutes. Description: %s"
    print(info_fmt % (schedule_entry["channel_id"], schedule_entry["duration_minutes"], schedule_entry["description"]))

    channel_data = get_atsc_channel(config["channels_filename"], schedule_entry["channel_id"])
    select_frequency(config["frontend_dev_filename"], channel_data.BroadcastFreqkHz)
    pids = mux_pids(channel_data.PID_A, channel_data.PID_B, channel_data.PID_C)
    set_mux_pids(config["demux_dev_filename"], pids)
    call_ffmpeg(config, schedule_entry)


def load_config():
    config_filename = "recording_schedule.json"
    config = json.load(open(config_filename, "r"))
    required_settings = ["channels_file", "adapter_id", "dvb_frontend_number", "dvb_demux_number", "schedule"]
    for key in required_settings:
        assert key in config

    v4l_wc = '/dev/v4l/by-id/%s*-video-index0' % (config["adapter_id"])
    v4l_symlink = glob.glob(v4l_wc)[0]
    config["v4l_dev"] = os.path.realpath(v4l_symlink)

    snd_ctl_wc = '/dev/snd/by-id/%s*' % (config["adapter_id"])
    snd_ctl_symlink = glob.glob(snd_ctl_wc)[0]
    snd_ctl_dev = os.path.realpath(snd_ctl_symlink)
    pcm_dev_wc = os.path.join(os.path.dirname(snd_ctl_dev), 'pcmC%sD*' % (snd_ctl_dev[-1]))
    config["snd_dev"] = glob.glob(pcm_dev_wc)[0]

    dvb_dev_dir_wc = '/dev/dvb/by-id/%s*' % (config["adapter_id"])
    try:
        dvb_dev_dir_symlink = glob.glob(dvb_dev_dir_wc)[0]
        dvb_dev_dir = os.path.realpath(dvb_dev_dir_symlink)
    except TypeError:
        dvb_dev_dir = '/dev/dvb/adapter0'
    config["frontend_dev"] = os.path.join(dvb_dev_dir, 'frontend%d' % (config["dvb_frontend_number"]))
    config["demux_dev"] = os.path.join(dvb_dev_dir, 'demux%d' % (config["dvb_demux_number"]))

    return config


def main():
    from_zone = pytz.timezone(open('/etc/timezone', 'r').read().strip())
    config = load_config()

    running = True
    while running:
        current_time = datetime.datetime.now(from_zone)

        for entry in config["schedule"]:
            if "datetime" in entry:
                # For date-time specific recordings
                scheduled_datetime = datetime.datetime.strptime(entry['datetime'], entry['dt_format'])
                if current_time >= scheduled_datetime:
                    end_dt = scheduled_datetime + datetime.timedelta(minutes=entry['duration_minutes'])
                    if current_time < end_dt:
                        start_recording(config, entry)
                        break
            else:
                # For weekly recurring recordings
                days_of_week = entry['days_of_week']
                sched_time = datetime.datetime.strptime(entry['time'], entry['t_format'])
                # Adjust the time to today's date for comparison
                today = current_time.replace(hour=sched_time.hour, minute=sched_time.minute, second=0, microsecond=0)
                weekdays = [datetime.datetime.strptime(day, '%a').weekday() for day in days_of_week]

                if current_time.weekday() in weekdays:
                    if current_time >= today:
                        end_dt = today + datetime.timedelta(minutes=entry['duration_minutes'])
                        if current_time < end_dt:
                            start_recording(config, entry)
                            break

        # Check every 10 seconds for the next scheduled event
        time.sleep(10)


if __name__ == "__main__":
    main()

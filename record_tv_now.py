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
import sys
from atsc_channels import get_atsc_channel
from adaptor_tuning import mux_pids, select_frequency, set_mux_pids
from ffmpeg_v4l_record import call_ffmpeg
from atsc_vcr import load_config, start_recording


def main():
    from_zone = pytz.timezone(open('/etc/timezone', 'r').read().strip())
    config = load_config()

    schedule = dict()
    schedule['datetime'] = datetime.datetime.now(from_zone)
    schedule["channel_id"] = '6-1' if len(sys.argv < 1) else sys.argv[1]
    schedule["duration_minutes"] = 60 if len(sys.argv) < 2 else int(sys.argv[2])
    schedule["description"] = '' if len(sys.argv) < 3 else sys.argv[3]

    start_recording(config, schedule)


if __name__ == "__main__":
    main()

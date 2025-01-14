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
from atsc_vcr import load_config, start_recording


def main():
    from_zone = pytz.timezone(open('/etc/timezone', 'r').read().strip())
    config = load_config()

    schedule = dict()
    schedule['datetime'] = datetime.datetime.now(from_zone)
    try:
        schedule["channel_id"] = sys.argv[1]
    except IndexError:
        schedule["channel_id"] = '6-1'
    try:
        schedule["duration_minutes"] = int(sys.argv[2])
    except IndexError:
        schedule["duration_minutes"] = 1
    try:
        schedule["description"] = sys.argv[3]
    except IndexError:
        schedule["description"] = ''

    start_recording(config, schedule)


if __name__ == "__main__":
    main()

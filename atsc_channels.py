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

import re
from collections import namedtuple

atsc_channel = None
required_columns = ["Channel", "Name", "Sequence #", "BroadcastFreq(kHz)", "PID_A", "PID_B", "PID_C"]


def get_atsc_channel(channels_filename: str, channel_id: str):
    global atsc_channel

    csv_file = open(channels_filename, "r")
    header = None
    fld_map = dict()
    channel = None
    channel_field_index = None
    seq_field_index = None

    for line in csv_file:
        fields = line.rstrip('\r\n').split(',')

        if header is None:
            header = fields
            for name in required_columns:
                assert name in header
            safe_header = list()
            for value in header:
                safe_name = re.sub(r'[^A-Za-z0-9_]', '', value)
                uniq_safe_name = safe_name + "_2" if safe_name in safe_header else safe_name
                safe_header.append(uniq_safe_name)
            for index, value in enumerate(safe_header):
                fld_map[value] = index
            channel_field_index = fld_map["Channel"]
            seq_field_index = fld_map["Sequence"]
            if atsc_channel is None:
                atsc_channel = namedtuple('atsc_channel', safe_header)
            continue

        if channel_id == fields[channel_field_index]:
            for index in range(seq_field_index, len(fields)):
                fields[index] = int(fields[index])
            channel = atsc_channel(* fields)
            break

    csv_file.close()
    return channel
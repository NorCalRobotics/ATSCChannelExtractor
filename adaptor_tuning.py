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

import os
import fcntl
import struct
from typing import Sequence
from collections import namedtuple

mux_pids = namedtuple('mux_pids', ['video', 'PCR', 'audio'])

# Structure for DVBv5 properties
class dtv_property:
    def __init__(self, cmd: int, udata: bytes):
        self.cmd = cmd
        self.reserved = [0] * 4
        self.u = udata


class dtv_properties:
    def __init__(self, num: int, props: Sequence[dtv_property]):
        self.num = num
        self.props = props


# Define the filter structure
class dmx_pes_filter_params:
    def __init__(self, pid: int, input: int, output: int, pes_type: int, flags: int):
        self.pid = pid
        self.input = input
        self.output = output
        self.pes_type = pes_type
        self.flags = flags


def select_frequency(dev_filename: str, hertz: int):
    # Open the frontend device file
    # Note: You might need to adjust '/dev/dvb/adapter0/frontend0' based on your system setup
    fd = os.open(dev_filename, os.O_RDWR)

    # Define constants (you'd typically get these from dvb/frontend.h or similar)
    FE_SET_PROPERTY = 0x80046604
    FE_GET_PROPERTY = 0xc0046605
    DTV_TUNE = 4  # From DVBv5 API

    # Create the property structure
    props = [
        dtv_property(DTV_TUNE, struct.pack('Q', hertz))  # Q for uint64_t
    ]

    # Pack properties into a dtv_properties structure for ioctl
    props_struct = dtv_properties(len(props), props)

    # Pack the entire structure for ioctl
    cmd_struct = struct.pack('I' + 'I6sQ' * len(props),
                             len(props),
                             *(prop.cmd for prop in props),
                             *([0] * 4 * len(props)),  # reserved
                             *(struct.unpack('Q', prop.u)[0] for prop in props))

    # Use FE_SET_PROPERTY to send the tuning command
    try:
        fcntl.ioctl(fd, FE_SET_PROPERTY, cmd_struct)
        print("Tuning command sent.")
    except IOError as e:
        print(f"Failed to tune: {e}")

    # Optionally, check if tuning was successful by reading back properties
    # This part is more complex and depends on what you want to verify after tuning

    # Close the file descriptor
    os.close(fd)

def set_mux_pids(dev_filename: str, pids: mux_pids):
    # DMX_SET_PES_FILTER ioctl command
    DMX_SET_PES_FILTER = 0x40046f20
    DMX_PES_AUDIO = 0
    DMX_PES_VIDEO = 1
    DMX_PES_PCR = 4

    # Open the frontend device file
    fd = os.open(dev_filename, os.O_RDWR)

    # Set up the filter for video or audio
    filter_params = dmx_pes_filter_params(
        pid=pids.audio,
        input=0,  # DMX_IN_FRONTEND
        output=1,  # DMX_OUT_TS_TAP
        pes_type=DMX_PES_AUDIO,
        flags=0  # No flags
    )

    # Pack the structure for ioctl
    filter_data = struct.pack('HIIIi', filter_params.pid, filter_params.input,
                              filter_params.output, filter_params.pes_type, filter_params.flags)

    # Apply the filter
    fcntl.ioctl(fd, DMX_SET_PES_FILTER, filter_data)

    # Set up the filter for video or audio
    filter_params.pid=pids.video
    filter_params.pes_type=DMX_PES_VIDEO

    # Pack the structure for ioctl
    filter_data = struct.pack('HIIIi', filter_params.pid, filter_params.input,
                              filter_params.output, filter_params.pes_type, filter_params.flags)

    # Apply the filter
    fcntl.ioctl(fd, DMX_SET_PES_FILTER, filter_data)

    # Set up the filter for video or audio
    filter_params.pid=pids.PCR
    filter_params.pes_type=DMX_PES_PCR

    # Pack the structure for ioctl
    filter_data = struct.pack('HIIIi', filter_params.pid, filter_params.input,
                              filter_params.output, filter_params.pes_type, filter_params.flags)

    # Apply the filter
    fcntl.ioctl(fd, DMX_SET_PES_FILTER, filter_data)

    # Close the file descriptor
    os.close(fd)

if __name__ == "__main__":
    # Tune to KVIEHD, Channel 6-1
    # Note: You might need to adjust '/dev/dvb/adapter0/frontend0' based on your system setup
    select_frequency('/dev/dvb/adapter0/frontend0', 187250000)
    set_mux_pids("/dev/dvb/adapter0/demux0", mux_pids(49, 48, 49))
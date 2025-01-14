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
import sys
import shutil
import subprocess
from typing import Sequence
from collections import namedtuple

mux_pids = namedtuple('mux_pids', ['video', 'PCR', 'audio'])

c_filename = 'adaptor_tuning.c'
bin_filename = 'adaptor_tuning'

def tune_to_atsc_channel(frontend_dev_filename: str, kHz: int, demux_dev_filename: str, pids: mux_pids):
    source_filename = os.path.join(sys.path[0], c_filename)
    binary_filename = os.path.join(sys.path[0], bin_filename)
    if not os.path.exists(binary_filename):
        subprocess.call([shutil.which('gcc'), source_filename, '-o', binary_filename]);

    subprocess.call([
        binary_filename,
        frontend_dev_filename,
        str(kHz),
        demux_dev_filename,
        str(pids.video),
        str(pids.PCR),
        str(pids.audio)
    ])

if __name__ == "__main__":
    # Tune to KVIEHD, Channel 6-1
    # Note: You might need to adjust '/dev/dvb/adapter0/frontend0' based on your system setup
    tune_to_atsc_channel('/dev/dvb/adapter0/frontend0', 187250000, "/dev/dvb/adapter0/demux0", mux_pids(49, 48, 49))

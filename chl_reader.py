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

import struct
import sys
import os

default_chl_filename = 'sample.chl'

modulation_scheme_name = {1: "8-VSB", 2: "16-VSB", 3: "256-QAM"}
identified_labels = {
    "CN1_1": "BroadcastFreq(kHz)",
    "CN1_2": "Bandwidth(mHz)",
    # These 3 are all still uncertain, but there's a strong chance that they are some kind of PID's
    "CN1_3": "PID_A", # "VideoPID",
    "CN1_4": "PID_B", # "PCR PID",
    "CN1_5": "PID_C", # "AudioPID",
    "CN1_15": "Digital TSID(FCC)",
    "CN1_16": "Digital Program Number",
    "CN1_17": "Digital Channel Number",
    "CN1_18": "Legacy Channel Number",
    "CN1_19": "Legacy Program Number",
    "CN3_0": "Sequence #"
}

# Target certain offsets based on analysis in hex editor:
pos_a = 1048
a_to_b = 1588 - pos_a
a_to_c = 2108 - pos_a
a_to_d = 2628 - pos_a
a_to_e = 3148 - pos_a
a_to_f = 3680 - pos_a
a_to_g = 3786 - pos_a
a_to_h = 4288 - pos_a
a_to_i = 4376 - pos_a


def read_utf16_string(stream):
    s = u''
    last_char = 1

    while last_char != 0:
        u16_char = struct.unpack('1h', stream.read(2))  # '1s' means 1 short integer
        s += chr(u16_char[0])
        last_char = u16_char[0]

    return s


def find_all_occurrences(f, pattern):
    """
    Finds all occurrences of a given pattern in a file.

    Args:
        file_path: Path to the file to search.
        pattern: The pattern to search for.

    Returns:
        A list of starting positions of the pattern in the file.
    """

    start = 0
    f.seek(start, os.SEEK_SET)
    data = f.read()
    f.seek(start, os.SEEK_SET)

    found = True
    positions = []
    while found:
        try:
            start = data.index(pattern, start)
            positions.append(start)
            start += len(pattern)
        except ValueError:
            found = False

    return positions


def main_per_channel(chl_file, fpos_A):
    # @1048 32b: 1, 1, 0, 1
    chl_file.seek(fpos_A, os.SEEK_SET) # Jump to position A
    i_chl_header = struct.unpack('4i', chl_file.read(16))

    # @1588 u: KVIEHD
    chl_file.seek(fpos_A + a_to_b, os.SEEK_SET) # Jump to position B
    chl_name = read_utf16_string(chl_file)

    # @2108 u: @device:pnp:\\?\usb#vid_1f4d&pid_a681# etc.
    chl_file.seek(fpos_A + a_to_c, os.SEEK_SET) # C
    win32_dev = read_utf16_string(chl_file)

    # @2628 u: Digital TV
    chl_file.seek(fpos_A + a_to_d, os.SEEK_SET) # D
    chl_type = read_utf16_string(chl_file)

    # @3148 u: KVIEHD
    chl_file.seek(fpos_A + a_to_e, os.SEEK_SET) # E
    chl_name2 = read_utf16_string(chl_file)

    # @3680 32b: 688, 187250, 6, 49, 48, 49, 1, 0,0,0,0,0,0,0,0, 345, 1, 9, 6, 1, 0, 2
    chl_file.seek(fpos_A + a_to_f, os.SEEK_SET) # F
    i_chl_numbers1 = struct.unpack('22i', chl_file.read(22 * 4))
    chl_num_s = str(i_chl_numbers1[18]) + '-' + str(i_chl_numbers1[19])
    dchl_num_s = str(i_chl_numbers1[17]) + '.' + str(i_chl_numbers1[16])
    mhz_s = str(float(i_chl_numbers1[1]) / 1000.0)

    # @3786 16b: 75, 86, 73, 69, 72, 68
    chl_file.seek(fpos_A + a_to_g, os.SEEK_SET) # G
    i_chl_numbers2 = struct.unpack('7h', chl_file.read(7 * 2))

    # @4288 32b: 1, 0,0, 23, 0,0,0,0,0,0, 24
    chl_file.seek(fpos_A + a_to_h, os.SEEK_SET) # H
    i_chl_numbers3 = struct.unpack('11i', chl_file.read(11 * 4))

    # @4376: [0x05][0x04]AC-3[0x81][\n][0x08]1[0x05][0xFF][0x01][0xBF]eng[\n][0x04]eng[\0]
    # chl_file.seek(fpos_A + a_to_i, os.SEEK_SET)
    # I have no idea what this stuff is,
    # other than AC-3 (Dolby Digital audio stream),
    # except perhaps "English" is being indicated twice

    # Channel,MHZ,Digital
    sys.stdout.write("%s,%s,%s," % (chl_num_s, mhz_s, dchl_num_s))
    # Name,Name2,Type,WIN32DEVICEID
    sys.stdout.write("%s,%s,%s,%s," % (chl_name, chl_name2, chl_type, win32_dev))
    # HN0-HN3
    sys.stdout.write(",".join([str(i) for i in i_chl_header]) + ",")
    # CN1_0-CN1_21
    sys.stdout.write(",".join([str(i) for i in i_chl_numbers1]) + ",")
    # CN2_0-CN2_6
    sys.stdout.write(",".join([str(i) for i in i_chl_numbers2]) + ",")
    # CN3_0-CN3_10
    sys.stdout.write(",".join([str(i) for i in i_chl_numbers3]) + "\n")


def main(chl_filename):
    chl_file = open(chl_filename, 'rb')
    # Read the first 8 4-byte sequences (32 bytes) and unpack them into integers
    # @0 32b: 1048, 2, 39, 2, 2632, 664, 8
    # 1048 --> this is the offset in the file where the 1st record began
    # 39   --> I found 39 records in the file
    i_header = struct.unpack('8i', chl_file.read(32))  # '8i' means 8 integers
    
    sys.stdout.write("Channel,mHz,Digital Channel,")
    sys.stdout.write("Name,Name2,Type,WIN32DEVICEID,")
    sys.stdout.write("Sequence #,HN1,HN2,HN3")

    for i in range(22):
        label = "CN1_%d" % (i)
        if label in identified_labels:
            label = identified_labels[label]
        sys.stdout.write("," + label)

    for i in range(7):
        label = "CN2_%d" % (i)
        if label in identified_labels:
            label = identified_labels[label]
        sys.stdout.write("," + label)

    for i in range(11):
        label = "CN3_%d" % (i)
        if label in identified_labels:
            label = identified_labels[label]
        sys.stdout.write("," + label)

    sys.stdout.write("\n")
    
    # Find offsets of all records in the file
    fpos_A = i_header[0]
    chl_file.seek(fpos_A + a_to_d, os.SEEK_SET) # D
    # @2628 u: Digital TV
    d_pattern = bytes(read_utf16_string(chl_file), 'utf-16le')
    chl_offsets = [ d_offset - a_to_d for d_offset in find_all_occurrences(chl_file, d_pattern) ]
    
    for fpos_A in chl_offsets:
        main_per_channel(chl_file, fpos_A)


if __name__ == '__main__':
    filenames = sys.argv[1:]
    if len(filenames) <= 0:
        filenames = [default_chl_filename]

    for filename in filenames:
        main(filename)

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

avconv \
  -f rawvideo \
  -pix_fmt yuyv422 \
  -s "${WIDTH:-640}x${HEIGHT:-480}" \
  -i "${VIDEO_FILE:-capture.yuyv}" \
  -f s16le \
  -ac 2 \
  -i "${AUDIO_FILE:-capture.wav}" \
  -c:v libx264 \
  -b:v "${BITRATE:-8M}" \
  -c:a aac \
  -b:a 128k \
  -preset ultrafast \
  "${OUTPUT_FILENAME:-program.mp4}"

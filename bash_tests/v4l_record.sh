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

V4L_VFMT="width=${WIDTH:-640},height=${HEIGHT:-480},pixelformat=YUYV"

v4l2-ctl \
  --device="${V4L_DEVICE:-/dev/video0}" \
  --set-fmt-video="$V4L_VFMT" \
  --stream-mmap \
  --stream-to="${1:-capture.yuyv}"

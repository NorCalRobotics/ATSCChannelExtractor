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

export VIDEO_FILE=video_pipe
export AUDIO_FILE=audio_pipe

mkfifo $VIDEO_FILE
mkfifo $AUDIO_FILE

bash av_encode.sh &
ENCODE_PID=$!

bash v4l_record.sh $VIDEO_FILE &
VIDEO_PID=$!

bash alsa_record.sh $AUDIO_FILE

kill -SIGINT $VIDEO_PID

rm $VIDEO_FILE $AUDIO_FILE


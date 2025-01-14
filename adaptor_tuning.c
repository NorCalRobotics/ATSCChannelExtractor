/*
 * Copyright (c) 2025 NorCal Robotics - All Rights Reserved.
 *
 * This source code is licensed under the MIT License.
 *
 * You may obtain a copy of the License at
 *
 *      https://opensource.org/licenses/MIT
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Author: Gabriel Field
 */

#include <linux/dvb/frontend.h>
#include <linux/dvb/dmx.h>
#include <sys/ioctl.h>
#include <assert.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char ** argv){
    struct dtv_property p[2];
    struct dtv_properties cmdseq;
    struct dmx_pes_filter_params pesFilterParams;
    char * frontend_dev_filename, * demux_dev_filename;
    int fd, kHz, pids[3], idx, ioctl_code;
    fe_status_t status;

    assert(argc == 7);
    frontend_dev_filename = argv[1];
    kHz = atoi(argv[2]);
    demux_dev_filename = argv[3];
    for(idx = 0; idx < 3; idx++){
        pids[idx] = atoi(argv[4 + idx]);
    }

    fd = open(frontend_dev_filename, O_RDWR);
    if (fd < 0) {
        perror("Failed to open frontend device");
        return -1;
    }

    p[0].cmd = DTV_CLEAR; // Clear all previous settings
    p[1].cmd = DTV_FREQUENCY;
    p[1].u.data = kHz;
    cmdseq.num = 2; // Number of properties to set
    cmdseq.props = p;

    ioctl_code = ioctl(fd, FE_SET_PROPERTY, &cmdseq);
    if (ioctl_code == -1) {
        perror("FE_SET_PROPERTY failed");
        close(fd);
        return -1;
    }

    ioctl_code = ioctl(fd, FE_GET_FRONTEND, &status);
    close(fd);
    if (ioctl_code == -1) {
        perror("FE_GET_FRONTEND failed");
        return -1;
    }

    fd = open(demux_dev_filename, O_RDWR);
    if (fd < 0) {
        perror("Failed to open demux device");
        return -1;
    }

    pesFilterParams.input = DMX_IN_FRONTEND;
    pesFilterParams.output = DMX_OUT_DECODER;
    pesFilterParams.flags = 0;  // No special flags

    pesFilterParams.pid = pids[0];
    pesFilterParams.pes_type = DMX_PES_VIDEO;
    ioctl_code = ioctl(fd, DMX_SET_PES_FILTER, &pesFilterParams);
    if (ioctl_code == -1) {
        perror("DMX_SET_PES_FILTER failed");
        close(fd);
        return -1;
    }

    pesFilterParams.pid = pids[1];
    pesFilterParams.pes_type = DMX_PES_PCR;
    ioctl_code = ioctl(fd, DMX_SET_PES_FILTER, &pesFilterParams);
    if (ioctl_code == -1) {
        perror("DMX_SET_PES_FILTER failed");
        close(fd);
        return -1;
    }

    pesFilterParams.pid = pids[2];
    pesFilterParams.pes_type = DMX_PES_AUDIO;
    ioctl_code = ioctl(fd, DMX_SET_PES_FILTER, &pesFilterParams);
    close(fd);
    if (ioctl_code == -1) {
        perror("DMX_SET_PES_FILTER failed");
        return -1;
    }

    return 0;
}

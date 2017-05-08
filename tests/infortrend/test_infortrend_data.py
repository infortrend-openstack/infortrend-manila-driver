# Copyright (c) 2017 Infortrend Technology, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


class InfortrendNASTestData(object):

    fake_service_status = ('(64175, 1234, 272, 0)\n\n'
                           '{"cliCode": '
                           '[{"Return": "0x0000", "CLI": "Successful"}], '
                           '"returnCode": [], '
                           '"data": '
                           '[{"A": '
                           '{"NFS": '
                           '{"displayName": "NFS", '
                           '"state_time": "2017-05-04 14:19:53", '
                           '"enabled": true, '
                           '"cpu_rate": "0.0", '
                           '"mem_rate": "0.0", '
                           '"state": "exited", '
                           '"type": "share"}}}]}\n\n')

    fake_folder_status = ('(64175, 1234, 1017, 0)\n\n'
                          '{"cliCode": '
                          '[{"Return": "0x0000", "CLI": "Successful"}], '
                          '"returnCode": [], '
                          '"data": '
                          '[{"utility": "1.00", '
                          '"used": "33886208", '
                          '"subshare": true, '
                          '"share": false, '
                          '"worm": "", '
                          '"free": "321931374592", '
                          '"fsType": "xfs", '
                          '"owner": "A", '
                          '"readOnly": false, '
                          '"modifyTime": "2017-04-27 16:16", '
                          '"directory": "/LV-1/share-pool-01", '
                          '"volumeId": "6541BAFB2E6C57B6", '
                          '"mounted": true, '
                          '"size": "321965260800"}, '
                          '{"utility": "1.00", '
                          '"used": "33779712", '
                          '"subshare": false, '
                          '"share": false, '
                          '"worm": "", '
                          '"free": "107287973888", '
                          '"fsType": "xfs", '
                          '"owner": "A", '
                          '"readOnly": false, '
                          '"modifyTime": "2017-04-27 15:45", '
                          '"directory": "/LV-1/share-pool-02", '
                          '"volumeId": "147A8FB67DA39914", '
                          '"mounted": true, '
                          '"size": "107321753600"}]}\n\n')

    fake_nfs_status_off = [{
        'A': {
            'NFS': {
                'displayName': 'NFS',
                'state_time': '2017-05-04 14:19:53',
                'enabled': False,
                'cpu_rate': '0.0',
                'mem_rate': '0.0',
                'state': 'exited',
                'type': 'share',
            }
        }
    }]

    def fake_get_channel_status(self, status='UP'):
        return [{
            'datalink': 'mgmt0',
            'status': 'UP',
            'typeConfig': 'DHCP',
            'IP': '172.27.112.125',
            'MAC': '00:d0:23:00:15:a6',
            'netmask': '255.255.240.0',
            'type': 'dhcp',
            'gateway': '172.27.127.254'}, {
            'datalink': 'CH0',
            'status': 'UP',
            'typeConfig': 'DHCP',
            'IP': '172.27.112.223',
            'MAC': '00:d0:23:80:15:a6',
            'netmask': '255.255.240.0',
            'type': 'dhcp',
            'gateway': '172.27.127.254'}, {
            'datalink': 'CH1',
            'status': status,
            'typeConfig': 'DHCP',
            'IP': '172.27.113.209',
            'MAC': '00:d0:23:40:15:a6',
            'netmask': '255.255.240.0',
            'type': 'dhcp',
            'gateway': '172.27.127.254'}, {
            'datalink': 'CH2',
            'status': 'DOWN',
            'typeConfig': 'DHCP',
            'IP': '',
            'MAC': '00:d0:23:c0:15:a6',
            'netmask': '',
            'type': '',
            'gateway': ''}, {
            'datalink': 'CH3',
            'status': 'DOWN',
            'typeConfig': 'DHCP',
            'IP': '',
            'MAC': '00:d0:23:20:15:a6',
            'netmask': '',
            'type': '',
            'gateway': ''}]










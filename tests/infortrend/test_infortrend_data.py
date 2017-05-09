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

    fake_service_status_data = ('(64175, 1234, 272, 0)\n\n'
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

    fake_folder_status_data = ('(64175, 1234, 1017, 0)\n\n'
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

    fake_folder_status = [{
        'utility': '1.00',
        'used': '33886208',
        'subshare': True,
        'share': False,
        'worm': '',
        'free': '321931374592',
        'fsType': 'xfs',
        'owner': 'A',
        'readOnly': False,
        'modifyTime': '2017-04-27 16:16',
        'directory': '/LV-1/share-pool-01',
        'volumeId': '6541BAFB2E6C57B6',
        'mounted': True,
        'size': '321965260800'}, {
        'utility': '1.00',
        'used': '33779712',
        'subshare': False,
        'share': False,
        'worm': '',
        'free': '107287973888',
        'fsType': 'xfs',
        'owner': 'A',
        'readOnly': False,
        'modifyTime': '2017-04-27 15:45',
        'directory': '/LV-1/share-pool-02',
        'volumeId': '147A8FB67DA39914',
        'mounted': True,
        'size': '107321753600',
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
            'gateway': '',
        }]

    fake_fquota_status = [{
        'quota': '10737418240',
        'used': '0',
        'name': 'manila-unmanage-test-manage',
        'type': 'subfolder',
        'id': '537178178'}, {
        'quota': '32212254720',
        'used': '0',
        'name': '4d6984fd-8572-4467-964f-24936a8c4ea2',
        'type': 'subfolder',
        'id': '805306752'}, {
        'quota': '53687091200',
        'used': '0',
        'name': 'a7b933e6-bb77-4823-a86f-f2c3ab41a8a5',
        'type': 'subfolder',
        'id': '69',
    }]

    fake_share_nfs = {
        'share_id': 'f54a7219-0a2b-4d70-8e2e-b63ba65701fd',
        'availability_zone': 'nova',
        'terminated_at': 'datetime.datetime(2017, 5, 8, 8, 27, 25)',
        'availability_zone_id': 'fd32d76d-b5a8-4c5c-93d7-8f09fc2a8ad3',
        'updated_at': 'datetime.datetime(2017, 5, 8, 8, 27, 25)',
        'share_network_id': None,
        'export_locations': [],
        'share_server_id': None,
        'snapshot_id': None,
        'deleted_at': None,
        'id': '5a0aa06e-1c57-4996-be46-b81e360e8866',
        'size': 10,
        'replica_state': None,
        'user_id': '4944594433f0405588928a4212964658',
        'export_location': '172.27.112.223:/LV-1/share-pool-01/'
                           'f54a7219-0a2b-4d70-8e2e-b63ba65701fd',
        'display_description': None,
        'consistency_group_id': None,
        'project_id': '0e63326c50a246ac81fa1a0c8e003d5b',
        'launched_at': 'datetime.datetime(2017, 5, 8, 8, 23, 33)',
        'scheduled_at': 'datetime.datetime(2017, 5, 8, 8, 23, 29)',
        'status': 'deleting',
        'share_type_id': '23d8c637-0192-47fa-b921-958f22ed772f',
        'deleted': 'False',
        'host': 'compute@ift-manila#share-pool-01',
        'access_rules_status': 'active',
        'display_name': 'test_share',
        'name': 'share-5a0aa06e-1c57-4996-be46-b81e360e8866',
        'created_at': 'datetime.datetime(2017, 5, 8, 8, 23, 29)',
        'share_proto': 'NFS',
        'is_public': False,
        'source_cgsnapshot_member_id': None
    }

    def fake_get_share_status_nfs(self, status=False):
        fake_share_status_nfs = [{
            'ftp': False,
            'cifs': False,
            'oss': False,
            'sftp': False,
            'nfs': status,
            'directory': '/LV-1/share-pool-01/'
                         '1699fbd9-cc92-42f5-9b82-1f9c0e8f7dde',
            'exist': True,
            'afp': False,
            'webdav': False
        }]
        if status:
            fake_share_status_nfs[0]['nfs_detail'] = {
                'hostList': [{
                    'uid': '65534',
                    'insecure': 'insecure',
                    'squash': 'all',
                    'access': 'ro',
                    'host': '*',
                    'gid': '65534',
                    'mode': 'async',
                    'no_subtree_check': 'no_subtree_check',
                }]
            }
        return fake_share_status_nfs

    fake_share_cifs = {
        'share_id': '524ac17d-ce1b-4a80-a4c4-eb33e5119a5b',
        'availability_zone': 'nova',
        'terminated_at': None,
        'availability_zone_id': 'fd32d76d-b5a8-4c5c-93d7-8f09fc2a8ad3',
        'updated_at': 'datetime.datetime(2017, 5, 9, 2, 28, 35)',
        'share_network_id': None,
        'export_locations': [],
        'share_server_id': None,
        'snapshot_id': None,
        'deleted_at': None,
        'id': 'aac4fe64-7a9c-472a-b156-9adbb50b4d29',
        'size': 15,
        'replica_state': None,
        'user_id': '4944594433f0405588928a4212964658',
        'export_location': None,
        'display_description': None,
        'consistency_group_id': None,
        'project_id': '0e63326c50a246ac81fa1a0c8e003d5b',
        'launched_at': None,
        'scheduled_at': 'datetime.datetime(2017, 5, 9, 2, 28, 35)',
        'status': 'creating',
        'share_type_id': '23d8c637-0192-47fa-b921-958f22ed772f',
        'deleted': 'False',
        'host': 'compute@ift-manila#share-pool-01',
        'access_rules_status': 'active',
        'display_name': 'test-cifs',
        'name': 'share-aac4fe64-7a9c-472a-b156-9adbb50b4d29',
        'created_at': 'datetime.datetime(2017, 5, 9, 2, 28, 35)',
        'share_proto': 'CIFS',
        'is_public': False,
        'source_cgsnapshot_member_id': None
    }

    def fake_get_share_status_cifs(self, status=False):
        fake_share_status_cifs = [{
            'ftp': False,
            'cifs': status,
            'oss': False,
            'sftp': False,
            'nfs': False,
            'directory': '/LV-1/share-pool-01/'
                         '524ac17d-ce1b-4a80-a4c4-eb33e5119a5b',
            'exist': True,
            'afp': False,
            'webdav': False
        }]
        if status:
            fake_share_status_cifs[0]['cifs_detail'] = {
                'available': True,
                'encrypt': False,
                'description': '',
                'sharename': 'test-cifs',
                'failover': '',
                'AIO': True,
                'priv': 'None',
                'recycle_bin': False,
                'ABE': True,
            }
        return fake_share_status_cifs












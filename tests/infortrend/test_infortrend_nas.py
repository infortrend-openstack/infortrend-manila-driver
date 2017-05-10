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

import mock
import ddt

from oslo_config import cfg
from manila import exception
from manila import test
from manila import context
from manila.share import configuration
from manila.share.drivers.infortrend import driver
from manila.share.drivers.infortrend import infortrend_nas
from manila.tests.share.drivers.infortrend import fake_infortrend_nas_data
from manila.tests.share.drivers.infortrend import fake_infortrend_manila_data

CONF = cfg.CONF

SUCCEED = (0, [])
FAILED = (-1, None)


@ddt.ddt
class InfortrendNASDriverTestCase(test.TestCase):
    def __init__(self, *args, **kwargs):
        super(InfortrendNASDriverTestCase, self).__init__(*args, **kwargs)
        self._ctxt = context.get_admin_context()
        self.nas_data = fake_infortrend_nas_data.InfortrendNASTestData()
        self.m_data = fake_infortrend_manila_data.InfortrendManilaTestData()

    def setUp(self):
        CONF.set_default('driver_handles_share_servers', False)
        CONF.set_default('infortrend_nas_ip', '172.27.1.1')
        CONF.set_default('infortrend_nas_user', 'fake_user')
        CONF.set_default('infortrend_nas_password', 'fake_password')
        CONF.set_default('infortrend_nas_ssh_key', 'fake_sshkey')
        CONF.set_default('infortrend_share_pools', 'share-pool-01')
        CONF.set_default('infortrend_share_channels', '0, 1')
        self.fake_conf = configuration.Configuration(None)
        super(InfortrendNASDriverTestCase, self).setUp()

    def _get_driver(self, fake_conf, init_dict=False):
        self._driver = driver.InfortrendNASDriver(
            configuration=fake_conf)
        self._iftnas = self._driver.ift_nas

        if init_dict:
            self._iftnas.pool_dict = {
                'share-pool-01': {
                    'id': '6541BAFB2E6C57B6',
                    'path': '/LV-1/share-pool-01',
                }
            }
            self._iftnas.channel_dict = {
                '0': self.nas_data.fake_channel_ip[0],
                '1': self.nas_data.fake_channel_ip[1],
            }

    def test_parser_with_service_status(self):
        expect_service_status = [{
            'A': {
                'NFS': {
                    'displayName': 'NFS',
                    'state_time': '2017-05-04 14:19:53',
                    'enabled': True,
                    'cpu_rate': '0.0',
                    'mem_rate': '0.0',
                    'state': 'exited',
                    'type': 'share',
                }
            }
        }]
        self._get_driver(self.fake_conf)
        rc, service_status = self._iftnas._parser(
            self.nas_data.fake_service_status_data)

        self.assertEqual(0, rc)
        self.assertDictListMatch(expect_service_status, service_status)

    def test_parser_with_folder_status(self):
        expect_folder_status = [{
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
            'size': '107321753600'}]

        self._get_driver(self.fake_conf)
        rc, folder_status = self._iftnas._parser(
            self.nas_data.fake_folder_status_data)

        self.assertEqual(0, rc)
        self.assertDictListMatch(expect_folder_status, folder_status)

    def test_ensure_service_on(self):
        self._get_driver(self.fake_conf)
        mock_execute = mock.Mock(
            side_effect=[(0, self.nas_data.fake_nfs_status_off), SUCCEED])
        self._iftnas._execute = mock_execute

        self._iftnas._ensure_service_on('nfs')
        mock_execute.assert_called_with(['service', 'restart', 'nfs'])

    def test_check_channels_status(self):
        expect_channel_dict = {
            '0': self.nas_data.fake_channel_ip[0],
            '1': self.nas_data.fake_channel_ip[1],
        }
        self._get_driver(self.fake_conf)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.nas_data.fake_get_channel_status()))

        self._iftnas._check_channels_status()
        self.assertDictMatch(expect_channel_dict, self._iftnas.channel_dict)

    @mock.patch.object(infortrend_nas.LOG, 'warning')
    def test_channel_status_down(self, log_warning):
        self._get_driver(self.fake_conf)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.nas_data.fake_get_channel_status('DOWN')))

        self._iftnas._check_channels_status()
        self.assertEqual(1, log_warning.call_count)

    @mock.patch.object(infortrend_nas.LOG, 'error')
    def test_invalid_channel(self, log_error):
        self.fake_conf.set_default('infortrend_share_channels', '0, 6')
        self._get_driver(self.fake_conf)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.nas_data.fake_get_channel_status()))

        self.assertRaises(
            exception.InfortrendNASException,
            self._iftnas._check_channels_status)

    def test_check_pools_setup(self):
        expect_pool_dict = {
            'share-pool-01': {
                'id': '6541BAFB2E6C57B6',
                'path': '/LV-1/share-pool-01',
            }
        }
        self._get_driver(self.fake_conf)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.nas_data.fake_folder_status))

        self._iftnas._check_pools_setup()

        self.assertDictMatch(expect_pool_dict, self._iftnas.pool_dict)

    def test_unknow_pools_setup(self):
        self.fake_conf.set_default(
            'infortrend_share_pools', 'chengwei, share-pool-01')
        self._get_driver(self.fake_conf)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.nas_data.fake_folder_status))

        self.assertRaises(
            exception.InfortrendNASException,
            self._iftnas._check_pools_setup)

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_get_pool_quota_used(self, mock_execute):
        self._get_driver(self.fake_conf, True)
        mock_execute.return_value = (0, self.nas_data.fake_fquota_status)

        pool_quota = self._iftnas._get_pool_quota_used('share-pool-01')

        mock_execute.assert_called_with(
            ['fquota', 'status', '6541BAFB2E6C57B6',
             'share-pool-01', '-t', 'folder'])
        self.assertEqual(107374182400, pool_quota)

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_create_share_nfs(self, mock_execute):
        fake_share_id = self.m_data.fake_share_nfs['share_id']
        expect_locations = [
            self.nas_data.fake_channel_ip[0] +
            ':/LV-1/share-pool-01/' + fake_share_id,
            self.nas_data.fake_channel_ip[1] +
            ':/LV-1/share-pool-01/' + fake_share_id,
        ]

        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            SUCCEED,  # create folder
            SUCCEED,  # set size
            (0, self.nas_data.fake_get_share_status_nfs()),  # check proto
            SUCCEED,  # enable proto
            (0, self.nas_data.fake_get_channel_status())  # update channel
        ]

        locations = self._driver.create_share(
            self._ctxt, self.m_data.fake_share_nfs)

        self.assertEqual(expect_locations, locations)
        mock_execute.assert_any_call(
            ['share', '/LV-1/share-pool-01/' + fake_share_id, 'nfs', 'on'])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_create_share_cifs(self, mock_execute):
        fake_share_id = self.m_data.fake_share_cifs['share_id']
        fake_display_name = self.m_data.fake_share_cifs['display_name']
        expect_locations = [
            '\\\\' + self.nas_data.fake_channel_ip[0] +
            '\\' + fake_display_name,
            '\\\\' + self.nas_data.fake_channel_ip[1] +
            '\\' + fake_display_name,
        ]

        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            SUCCEED,  # create folder
            SUCCEED,  # set size
            (0, self.nas_data.fake_get_share_status_cifs()),  # check proto
            SUCCEED,  # enable proto
            (0, self.nas_data.fake_get_channel_status())  # update channel
        ]

        locations = self._driver.create_share(
            self._ctxt, self.m_data.fake_share_cifs)

        self.assertEqual(expect_locations, locations)
        mock_execute.assert_any_call(
            ['share', '/LV-1/share-pool-01/' + fake_share_id,
             'cifs', 'on', '-n', fake_display_name])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_delete_share_nfs(self, mock_execute):
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            (0, self.nas_data.fake_subfolder_data),  # pagelist folder
            SUCCEED,  # delete folder
        ]

        self._driver.delete_share(
            self._ctxt, self.m_data.fake_share_nfs)

        mock_execute.assert_any_call(
            ['folder', 'options', '6541BAFB2E6C57B6', 'share-pool-01',
             '-d', self.m_data.fake_share_nfs['share_id']])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_delete_share_cifs(self, mock_execute):
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            (0, self.nas_data.fake_subfolder_data),  # pagelist folder
            SUCCEED,  # delete folder
        ]

        self._driver.delete_share(
            self._ctxt, self.m_data.fake_share_cifs)

        mock_execute.assert_any_call(
            ['folder', 'options', '6541BAFB2E6C57B6', 'share-pool-01',
             '-d', self.m_data.fake_share_cifs['share_id']])

    @mock.patch.object(infortrend_nas.LOG, 'warning')
    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_delete_non_exist_share(self, mock_execute, log_warning):
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            (0, self.nas_data.fake_subfolder_data),  # pagelist folder
        ]

        self._driver.delete_share(
            self._ctxt, self.m_data.fake_non_exist_share)

        self.assertEqual(1, log_warning.call_count)

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_update_access_nfs_add_rule(self, mock_execute):
        share_id = self.m_data.fake_share_nfs['share_id']
        share_path = '/LV-1/share-pool-01/' + share_id
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            SUCCEED,
        ]

        self._driver.update_access(
            self._ctxt,
            self.m_data.fake_share_nfs,
            self.m_data.fake_access_rules_nfs,
            self.m_data.fake_rule_ip_2,
            [],
        )

        mock_execute.assert_called_once_with(
            ['share', 'options', share_path,
             'nfs', '-h', '172.27.1.2', '-p', 'rw'])

    def test_update_access_nfs_wrong_rule(self):
        self._get_driver(self.fake_conf, True)

        self.assertRaises(
            exception.InvalidShareAccess,
            self._driver.update_access,
            self._ctxt,
            self.m_data.fake_share_nfs,
            self.m_data.fake_access_rules_nfs,
            self.m_data.fake_rule_user01,
            [])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_update_access_nfs_delete_rule(self, mock_execute):
        share_id = self.m_data.fake_share_nfs['share_id']
        share_path = '/LV-1/share-pool-01/' + share_id
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            SUCCEED,
        ]

        self._driver.update_access(
            self._ctxt,
            self.m_data.fake_share_nfs,
            self.m_data.fake_access_rules_nfs,
            [],
            self.m_data.fake_rule_ip_1,
        )

        mock_execute.assert_called_once_with(
            ['share', 'options', share_path,
             'nfs', '-c', '172.27.1.1'])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_update_access_cifs_add_user_rw(self, mock_execute):
        share_id = self.m_data.fake_share_cifs['share_id']
        share_path = '/LV-1/share-pool-01/' + share_id
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            (0, self.nas_data.fake_cifs_user_list),  # check user exist
            SUCCEED,
        ]

        self._driver.update_access(
            self._ctxt,
            self.m_data.fake_share_cifs,
            self.m_data.fake_access_rules_cifs,
            self.m_data.fake_rule_user01,
            [],
        )

        mock_execute.assert_has_calls([
            mock.call(['useradmin', 'user', 'list']),
            mock.call(['acl', 'set', share_path,
                       '-u', 'user01', '-a', 'f'])
        ])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_update_access_cifs_add_user_ro(self, mock_execute):
        share_id = self.m_data.fake_share_cifs['share_id']
        share_path = '/LV-1/share-pool-01/' + share_id
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            (0, self.nas_data.fake_cifs_user_list),  # check user exist
            SUCCEED,
        ]

        self._driver.update_access(
            self._ctxt,
            self.m_data.fake_share_cifs,
            self.m_data.fake_access_rules_cifs,
            self.m_data.fake_rule_user02,
            [],
        )

        mock_execute.assert_has_calls([
            mock.call(['useradmin', 'user', 'list']),
            mock.call(['acl', 'set', share_path,
                       '-u', 'user02', '-a', 'r'])
        ])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_update_access_cifs_user_not_exist(self, mock_execute):
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            (0, self.nas_data.fake_cifs_user_list),  # check user exist
        ]

        self.assertRaises(
            exception.InfortrendNASException,
            self._driver.update_access,
            self._ctxt,
            self.m_data.fake_share_cifs,
            self.m_data.fake_access_rules_cifs,
            self.m_data.fake_rule_user03,
            [])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_update_access_cifs_delete_rule(self, mock_execute):
        share_id = self.m_data.fake_share_cifs['share_id']
        share_path = '/LV-1/share-pool-01/' + share_id
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            (0, self.nas_data.fake_cifs_user_list),  # check user exist
            SUCCEED,
        ]

        self._driver.update_access(
            self._ctxt,
            self.m_data.fake_share_cifs,
            self.m_data.fake_access_rules_cifs,
            [],
            self.m_data.fake_rule_user01,
        )

        mock_execute.assert_has_calls([
            mock.call(['useradmin', 'user', 'list']),
            mock.call(['acl', 'set', share_path,
                       '-u', 'user01', '-a', 'd'])
        ])

    def test_update_access_cifs_wrong_rule(self):
        self._get_driver(self.fake_conf, True)

        self.assertRaises(
            exception.InvalidShareAccess,
            self._driver.update_access,
            self._ctxt,
            self.m_data.fake_share_cifs,
            self.m_data.fake_access_rules_cifs,
            self.m_data.fake_rule_ip_1,
            [])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_clear_access_nfs(self, mock_execute):
        share_id = self.m_data.fake_share_nfs['share_id']
        share_path = '/LV-1/share-pool-01/' + share_id
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            (0, self.nas_data.fake_share_status_nfs_with_rules),
            SUCCEED,  # clear access
            SUCCEED,
            SUCCEED,  # allow access
            SUCCEED,
        ]

        self._driver.update_access(
            self._ctxt,
            self.m_data.fake_share_nfs,
            self.m_data.fake_access_rules_nfs,
            [],
            [],
        )

        mock_execute.assert_has_calls([
            mock.call(['share', 'status', '-f', share_path]),
            mock.call(['share', 'options', share_path,
                       'nfs', '-c', '172.27.1.1']),
            mock.call(['share', 'options', share_path,
                       'nfs', '-c', '172.27.1.2']),
            mock.call(['share', 'options', share_path,
                       'nfs', '-h', '172.27.1.1', '-p', 'rw']),
            mock.call(['share', 'options', share_path,
                       'nfs', '-h', '172.27.1.2', '-p', 'rw']),
        ])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_clear_access_cifs(self, mock_execute):
        share_id = self.m_data.fake_share_cifs['share_id']
        share_path = '/LV-1/share-pool-01/' + share_id
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            (0, self.nas_data.fake_share_status_cifs_with_rules),
            SUCCEED,  # clear user01
            SUCCEED,  # clear user02
            (0, self.nas_data.fake_cifs_user_list),
            SUCCEED,  # allow user02
            (0, self.nas_data.fake_cifs_user_list),
            SUCCEED,  # allow user01
        ]

        self._driver.update_access(
            self._ctxt,
            self.m_data.fake_share_cifs,
            self.m_data.fake_access_rules_cifs,
            [],
            [],
        )

        mock_execute.assert_has_calls([
            mock.call(['acl', 'get', share_path]),
            mock.call(['acl', 'set', share_path,
                       '-u', 'user01', '-a', 'd']),
            mock.call(['acl', 'set', share_path,
                       '-u', 'user02', '-a', 'd']),
            mock.call(['useradmin', 'user', 'list']),
            mock.call(['acl', 'set', share_path,
                       '-u', 'user02', '-a', 'r']),
            mock.call(['useradmin', 'user', 'list']),
            mock.call(['acl', 'set', share_path,
                       '-u', 'user01', '-a', 'f']),
        ])

    def test_get_pool(self):
        self._get_driver(self.fake_conf, True)
        pool = self._driver.get_pool(self.m_data.fake_share_nfs)

        self.assertEqual('share-pool-01', pool)

    def test_get_pool_without_host(self):
        self._get_driver(self.fake_conf, True)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.nas_data.fake_subfolder_data))

        pool = self._driver.get_pool(self.m_data.fake_share_cifs_no_host)
        self.assertEqual('share-pool-01', pool)

    def test_ensure_share_nfs(self):
        share_id = self.m_data.fake_share_nfs['share_id']
        share_path = '/LV-1/share-pool-01/' + share_id
        expect_locations = [
            self.nas_data.fake_channel_ip[0] + ':' + share_path,
            self.nas_data.fake_channel_ip[1] + ':' + share_path,
        ]
        self._get_driver(self.fake_conf, True)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.nas_data.fake_get_channel_status()))

        locations = self._driver.ensure_share(
            self._ctxt, self.m_data.fake_share_nfs)
        self.assertEqual(expect_locations, locations)

    def test_ensure_share_cifs(self):
        fake_display_name = self.m_data.fake_share_cifs['display_name']
        expect_locations = [
            '\\\\' + self.nas_data.fake_channel_ip[0] +
            '\\' + fake_display_name,
            '\\\\' + self.nas_data.fake_channel_ip[1] +
            '\\' + fake_display_name,
        ]
        self._get_driver(self.fake_conf, True)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.nas_data.fake_get_channel_status()))

        locations = self._driver.ensure_share(
            self._ctxt, self.m_data.fake_share_cifs)
        self.assertEqual(expect_locations, locations)

    def test_extend_share(self):
        share_id = self.m_data.fake_share_nfs['share_id']
        self._get_driver(self.fake_conf, True)
        self._iftnas._execute = mock.Mock(return_value=SUCCEED)

        self._driver.extend_share(self.m_data.fake_share_nfs, 100)

        self._iftnas._execute.assert_called_once_with(
            ['fquota', 'create', '6541BAFB2E6C57B6', 'share-pool-01',
             share_id, '100G', '-t', 'folder'])

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_manage_existing_nfs(self, mock_execute):
        share_id = self.m_data.fake_share_for_manage['share_id']
        pool_path = '/LV-1/share-pool-01'
        origin_share_path = pool_path + '/' + 'test-folder'
        export_share_path = pool_path + '/' + share_id
        expect_result = {
            'size': 20.0,
            'export_locations': [
                self.nas_data.fake_channel_ip[0] + ':' + export_share_path,
                self.nas_data.fake_channel_ip[1] + ':' + export_share_path,
            ]
        }
        self._get_driver(self.fake_conf, True)
        mock_execute.side_effect = [
            (0, self.nas_data.fake_subfolder_data),  # pagelist folder
            (0, self.nas_data.fake_get_share_status_nfs()),  # check proto
            SUCCEED,  # enable nfs
            (0, self.nas_data.fake_fquota_status),  # get share size
            SUCCEED,  # rename share
            (0, self.nas_data.fake_get_channel_status())  # update channel
        ]

        result = self._driver.manage_existing(
            self.m_data.fake_share_for_manage,
            {}
        )

        self.assertEqual(expect_result, result)
        mock_execute.assert_has_calls([
            mock.call(['pagelist', 'folder', pool_path]),
            mock.call(['share', 'status', '-f', origin_share_path]),
            mock.call(['share', origin_share_path, 'nfs', 'on']),
            mock.call(['fquota', 'status', '6541BAFB2E6C57B6',
                       'share-pool-01', '-t', 'folder']),
            mock.call(['folder', 'options', '6541BAFB2E6C57B6',
                       'share-pool-01', '-e', 'test-folder', share_id]),
            mock.call(['ifconfig', 'inet', 'show']),
        ])

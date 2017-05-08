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

import copy
import mock
import ddt

from oslo_config import cfg
from manila import exception
from manila import test
from manila import context
from manila.share import configuration
from manila.share.drivers.infortrend import driver
from manila.share.drivers.infortrend import infortrend_nas
from manila.tests.share.drivers.infortrend import test_infortrend_data
from manila.tests import fake_share

CONF = cfg.CONF


@ddt.ddt
class InfortrendNASDriverTestCase(test.TestCase):
    def __init__(self, *args, **kwargs):
        super(InfortrendNASDriverTestCase, self).__init__(*args, **kwargs)
        self._ctxt = context.get_admin_context()
        self.cli_data = test_infortrend_data.InfortrendNASTestData()

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

    def _get_driver(self, fake_conf):
        self._driver = driver.InfortrendNASDriver(
            configuration=fake_conf)
        self._iftnas = self._driver.ift_nas

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
            self.cli_data.fake_service_status_data)

        self.assertEqual(0, rc)
        self.assertEqual(expect_service_status, service_status)

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
            self.cli_data.fake_folder_status_data)

        self.assertEqual(0, rc)
        self.assertEqual(expect_folder_status, folder_status)

    def test_ensure_service_on(self):
        self._get_driver(self.fake_conf)
        mock_execute = mock.Mock(
            side_effect=[(0, self.cli_data.fake_nfs_status_off), []])
        self._iftnas._execute = mock_execute

        self._iftnas._ensure_service_on('nfs')
        mock_execute.assert_called_with(['service', 'restart', 'nfs'])

    def test_check_channels_status(self):
        expect_channel_dict = {
            '0': '172.27.112.223',
            '1': '172.27.113.209',
        }
        self._get_driver(self.fake_conf)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.cli_data.fake_get_channel_status()))

        self._iftnas._check_channels_status()
        self.assertEqual(expect_channel_dict, self._iftnas.channel_dict)

    @mock.patch.object(infortrend_nas.LOG, 'warning')
    def test_channel_status_down(self, log_warning):
        self._get_driver(self.fake_conf)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.cli_data.fake_get_channel_status('DOWN')))

        self._iftnas._check_channels_status()
        self.assertEqual(1, log_warning.call_count)

    @mock.patch.object(infortrend_nas.LOG, 'error')
    def test_invalid_channel(self, log_error):
        self.fake_conf.set_default('infortrend_share_channels', '0, 6')
        self._get_driver(self.fake_conf)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.cli_data.fake_get_channel_status()))

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
            return_value=(0, self.cli_data.fake_folder_status))

        self._iftnas._check_pools_setup()

        self.assertEqual(expect_pool_dict, self._iftnas.pool_dict)

    def test_unknow_pools_setup(self):
        self.fake_conf.set_default('infortrend_share_pools', 'chengwei')
        self._get_driver(self.fake_conf)
        self._iftnas._execute = mock.Mock(
            return_value=(0, self.cli_data.fake_folder_status))

        self.assertRaises(
            exception.InfortrendNASException,
            self._iftnas._check_pools_setup)

    @mock.patch.object(infortrend_nas.InfortrendNAS, '_execute')
    def test_get_pool_quota_used(self, mock_execute):
        self._get_driver(self.fake_conf)
        mock_execute.return_value = (0, self.cli_data.fake_fquota_status)
        self._iftnas.pool_dict = {
            'share-pool-01': {
                'id': '6541BAFB2E6C57B6',
                'path': '/LV-1/share-pool-01',
            }
        }

        pool_quota = self._iftnas._get_pool_quota_used('share-pool-01')

        mock_execute.assert_called_with(
            ['fquota', 'status', '6541BAFB2E6C57B6',
             'share-pool-01', '-t', 'folder'])
        self.assertEqual(96636764160, pool_quota)










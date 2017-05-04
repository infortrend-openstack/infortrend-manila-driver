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

from oslo_config import cfg
from manila import exception
from manila import test
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
        self.fake_conf = test_config
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
        self._driver = driver.InfortrendNASDriver(
            configuration=self.fake_conf)
        super(InfortrendNASDriverTestCase, self).setUp()

    def test_do_setup_with_service_off(self):
        self._driver.ift_nas._ensure_service_on('nfs')
        self._driver.ift_nas._execute = mock.Mock(
            return_value=self.cli_data.fake_service_status_nfs)
        self._driver.ift_nas._execute.assert_called_once_with(
            'service', 'restart', 'nfs')

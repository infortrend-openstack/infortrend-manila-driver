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


from oslo_log import log

from manila.share import driver
from manila.share.drivers.infortrend import infortrend_common

LOG = log.getLogger(__name__)


class InfortrendNASDriver(driver.ShareDriver):

    """Infortrend Fibre Channel Driver for Eonstor DS using CLI.

    Version history:
    	1.0.0 - Initial driver
    """

    VERSION = "1.0.0"

    def __init__(self, *args, **kwargs):
    	super(InfortrendNASDriver, self).__init__(False, *args, **kwargs)
        self.common = infortrend_common.InfortrendCommonClass(
        	configuration=self.configuration)

    def update_access(self, context, share, access_rules, add_rules,
                      delete_rules, share_server=None):
        """Update access rules for given share.

        Drivers should support 2 different cases in this method:
        1. Recovery after error - 'access_rules' contains all access_rules,
        'add_rules' and 'delete_rules' shall be empty. Driver should clear any
        existent access rules and apply all access rules for given share.
        This recovery is made at driver start up.

        2. Adding/Deleting of several access rules - 'access_rules' contains
        all access_rules, 'add_rules' and 'delete_rules' contain rules which
        should be added/deleted. Driver can ignore rules in 'access_rules' and
        apply only rules from 'add_rules' and 'delete_rules'.

        Drivers must be mindful of this call for share replicas. When
        'update_access' is called on one of the replicas, the call is likely
        propagated to all replicas belonging to the share, especially when
        individual rules are added or removed. If a particular access rule
        does not make sense to the driver in the context of a given replica,
        the driver should be careful to report a correct behavior, and take
        meaningful action. For example, if R/W access is requested on a
        replica that is part of a "readable" type replication; R/O access
        may be added by the driver instead of R/W. Note that raising an
        exception *will* result in the access_rules_status on the replica,
        and the share itself being "out_of_sync". Drivers can sync on the
        valid access rules that are provided on the ``create_replica`` and
        ``promote_replica`` calls.

        :param context: Current context
        :param share: Share model with share data.
        :param access_rules: All access rules for given share
        :param add_rules: Empty List or List of access rules which should be
               added. access_rules already contains these rules.
        :param delete_rules: Empty List or List of access rules which should be
               removed. access_rules doesn't contain these rules.
        :param share_server: None or Share server model
        :returns: None, or a dictionary of ``access_id``, ``access_key`` as
                  key: value pairs for the rules added, where, ``access_id``
                  is the UUID (string) of the access rule, and ``access_key``
                  is the credential (string) of the entity granted access.
                  During recovery after error, the returned dictionary must
                  contain ``access_id``, ``access_key`` for all the rules that
                  the driver is ordered to resync, i.e. rules in the
                  ``access_rules`` parameter.
        """
        LOG.debug(
            'update access rules for share: %(share)s, '
            'access_rules: %(access_rules)s, '
            'add_rules: %(add_rules)s, '
            'delete_rules: %(delete_rules)s,', {
                'share': share, 'access_rules': access_rules,
                'add_rules': add_rules, 'delete_rules': delete_rules})
        return self.common.update_access(context, share, access_rules,
        								 add_rules, delete_rules, share_server)

    def do_setup(self, context):
        """Any initialization the share driver does while starting."""
        LOG.debug('do_setup start')
        self.common.do_setup()

    def check_for_setup_error(self):
        """Check for setup error."""
        LOG.debug('check_for_setup_error start')
        max_ratio = self.configuration.safe_get('max_over_subscription_ratio')
        if not max_ratio or float(max_ratio) < 1.0:
            msg = (_("Invalid max_over_subscription_ratio '%s'. "
                     "Valid value should be >= 1.0.") % max_ratio)
            raise exception.InvalidParameterValue(err=msg)

        self.common.check_for_setup_error()

    def get_share_stats(self, refresh=False):
        """Get share status.

        If 'refresh' is True, run update the stats first.
        """
        if not self._stats or refresh:
            self._update_share_stats()

        return self._stats

    def _update_share_stats(self, data=None):
        """Retrieve stats info from share group.

        :param data: dict -- dict with key-value pairs to redefine common ones.
        """

        LOG.debug("Updating share stats.")

        common = self.common._update_share_stats()

        if isinstance(data, dict):
            common.update(data)
        self._stats = common



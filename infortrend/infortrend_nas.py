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

import json

from oslo_log import log
from oslo_utils import units
from oslo_concurrency import processutils

from manila.common import constants
from manila import exception
from manila.i18n import _
from manila import utils as manila_utils
from manila.share import utils as share_utils

LOG = log.getLogger(__name__)
DEFAULT_RETRY_TIME = 5


def retry_cli(func):
    def inner(self, *args, **kwargs):
        total_retry_time = self.cli_retry_time

        if total_retry_time is None:
            total_retry_time = DEFAULT_RETRY_TIME

        retry_time = 0
        while retry_time < total_retry_time:
            rc, out = func(self, *args, **kwargs)
            retry_time += 1

            if rc == 0:
                break

            LOG.error(
                'Retry %(retry)s times: %(command)s Failed '
                '%(rc)s: %(reason)s', {
                    'retry': retry_time,
                    'command': args,
                    'rc': rc,
                    'reason': out})
        LOG.debug(
            'Command: %(command)s Return Code: %(rc)s '
            'Output: %(out)s', {
                'command': args, 'rc': rc, 'out': out})
        return rc, out
    return inner


def bi_to_gi(bi_size):
    return bi_size / units.Gi


class InfortrendNAS(object):

    UNMANAGE_PREFIX = 'manila-unmanage-%s'

    def __init__(self, nas_ip, username, password, ssh_key,
                 retries, timeout, pool_dict, channel_dict):
        self.nas_ip = nas_ip
        self.port = 22
        self.username = username
        self.password = password
        self.ssh_key = ssh_key
        self.cli_retry_time = retries
        self.cli_timeout = timeout
        self.pool_dict = pool_dict
        self.channel_dict = channel_dict
        self.command = ""
        self.ssh = None
        self.sshpool = None
        self.location = 'a@0'

    def _execute(self, command_line):
        command_line.extend(['-z', self.location])
        commands = ' '.join(command_line)
        manila_utils.check_ssh_injection(commands)
        LOG.debug('Executing: %(command)s', {'command': commands})

        rc, out = self._ssh_execute(commands)

        if rc != 0:
            raise exception.InfortrendNASException(err=out)

        return self._parser(out)

    @retry_cli
    def _ssh_execute(self, commands):
        if not (self.sshpool and self.ssh):
            self.sshpool = manila_utils.SSHPool(ip=self.nas_ip,
                                                port=self.port,
                                                conn_timeout=None,
                                                login=self.username,
                                                password=self.password,
                                                privatekey=self.ssh_key)
            self.ssh = self.sshpool.create()

        if not self.ssh.get_transport().is_active():
            self.sshpool.remove(self.ssh)
            self.ssh = self.sshpool.create()

        try:
            out, err = processutils.ssh_execute(
                self.ssh, commands,
                timeout=self.cli_timeout, check_exit_code=True)
            rc = 0
        except processutils.ProcessExecutionError as pe:
            rc = pe.exit_code
            out = pe.stdout
            out = out.replace('\n', '\\n')
            LOG.error(_('Error on execute ssh command. '
                        'Error code: %(exit_code)d Error msg: %(out)s') % {
                            'exit_code': rc, 'out': out})

        return rc, out

    def _parser(self, content=None):
        content = content.replace("\r", "")
        content = content.strip()
        json_string = content.replace("'", "\"")
        cli_data = json_string.split("\n")[2]

        if cli_data:
            try:
                data_dict = json.loads(cli_data)
            except:
                msg = _('Failed to parse data: '
                        '%(cli_data)s to dictionary.') % {
                            'cli_data': cli_data}
                LOG.error(msg)
                raise exception.InfortrendNASException(err=msg)

            rc = int(data_dict['cliCode'][0]['Return'], 16)
            if rc == 0:
                result = data_dict['data']
            else:
                result = data_dict['cliCode'][0]['CLI']
        else:
            msg = _('No data is returned from NAS.')
            LOG.error(msg)
            raise exception.InfortrendNASException(err=msg)

        if rc != 0:
            msg = _('NASCLI error, returned: %(result)s.') % {
                'result': result}
            LOG.error(msg)
            raise exception.InfortrendCLIException(
                err=msg, rc=rc, out=result)

        return rc, result

    def do_setup(self):
        self._ensure_service_on('nfs')
        self._ensure_service_on('cifs')

    def check_for_setup_error(self):
        self._check_pools_setup()
        self._check_channels_status()

    def _ensure_service_on(self, proto, slot='A'):
        command_line = ['service', 'status', proto]
        rc, service_status = self._execute(command_line)
        if not service_status[0][slot][proto.upper()]['enabled']:
            command_line = ['service', 'restart', proto]
            self._execute(command_line)

    def _check_channels_status(self):
        channel_list = list(self.channel_dict.keys())
        command_line = ['ifconfig', 'inet', 'show']
        rc, channels_status = self._execute(command_line)
        for channel in channels_status:
            if 'CH' in channel['datalink']:
                ch = channel['datalink'].strip('CH')
                if ch in self.channel_dict.keys():
                    self.channel_dict[ch] = channel['IP']
                    channel_list.remove(ch)
                    if channel['status'] == 'DOWN':
                        LOG.warning('Channel [%(ch)s] status '
                                    'is down, please check.', {
                                        'ch': ch})
        if len(channel_list) != 0:
            msg = _('Channel setting %(channel_list)s is invalid!') % {
                'channel_list': channel_list}
            LOG.error(msg)
            raise exception.InfortrendNASException(message=msg)

    def _check_pools_setup(self):
        pool_list = self.pool_dict.keys()
        command_line = ['folder', 'status']
        rc, pool_data = self._execute(command_line)
        for pool_info in pool_data:
            pool_name = self._extract_pool_name(pool_info)
            if pool_name in self.pool_dict.keys():
                pool_list.remove(pool_name)
                self.pool_dict[pool_name]['id'] = pool_info['volumeId']
                self.pool_dict[pool_name]['path'] = pool_info['directory']
            if len(pool_list) == 0:
                break

        if len(pool_list) != 0:
            msg = _('Please create %(pool_list)s pool in advance!') % {
                'pool_list': pool_list}
            LOG.error(msg)
            raise exception.InfortrendNASException(message=msg)

    def _extract_pool_name(self, pool_info):
        return pool_info['directory'].split('/')[2]

    def _extract_lv_name(self, pool_info):
        return pool_info['directory'].split('/')[1]

    def update_pools_stats(self):
        pools = []
        command_line = ['folder', 'status']
        rc, pools_data = self._execute(command_line)

        for pool_info in pools_data:
            pool_name = self._extract_pool_name(pool_info)

            if pool_name in self.pool_dict.keys():
                total_space = float(pool_info['size'])
                pool_quota_used = self._get_pool_quota_used(pool_name)
                available_space = total_space - pool_quota_used

                total_capacity_gb = round(bi_to_gi(total_space), 2)
                free_capacity_gb = round(bi_to_gi(available_space), 2)

                pool = {
                    'pool_name': pool_name,
                    'total_capacity_gb': total_capacity_gb,
                    'free_capacity_gb': free_capacity_gb,
                    'reserved_percentage': 0,
                    'qos': False,
                    'dedupe': False,
                    'compression': False,
                    'snapshot_support': False,
                    'thin_provisioning': False,
                    'replication_type': None,
                }
                pools.append(pool)

        return pools

    def _get_pool_quota_used(self, pool_name):
        pool_quota_used = 0
        pool_id = self.pool_dict[pool_name]['id']

        command_line = ['fquota', 'status', pool_id,
                        pool_name, '-t', 'folder']
        rc, quota_status = self._execute(command_line)

        for share_quota in quota_status:
            pool_quota_used += int(share_quota['quota'])

        return pool_quota_used

    def create_share(self, share, share_server=None):
        pool_name = share_utils.extract_host(share['host'], level='pool')
        pool_id = self.pool_dict[pool_name]['id']
        pool_path = self.pool_dict[pool_name]['path']
        share_proto = share['share_proto'].lower()
        share_path = pool_path + '/' + share['share_id']
        display_name = share['display_name']

        command_line = ['folder', 'options', pool_id,
                        pool_name, '-c', share['share_id']]
        self._execute(command_line)

        self._set_share_size(
            pool_id, pool_name, share['share_id'], share['size'])
        self._ensure_protocol_on(share_path, share_proto, display_name)

        LOG.info('Create Share [%(share_id)s] completed.', {
            'share_id': share['share_id']})

        return self._export_location(share, share_proto, pool_path)

    def _export_location(self, share, share_proto, pool_path=None):
        location = []
        location_data = {
            'pool_path': pool_path,
            'id': share['share_id'],
            'name': share['display_name'],
        }
        self._check_channels_status()
        for ch in sorted(self.channel_dict.keys()):
            ip = self.channel_dict[ch]
            if share_proto == 'nfs':
                location.append(ip + ':%(pool_path)s/%(id)s' % location_data)
            elif share_proto == 'cifs':
                location.append('\\\\' + ip + '\\%(name)s' % location_data)
            else:
                msg = _('Unsupported protocol: [%s].') % share_proto
                raise exception.InvalidInput(msg)

        return location

    def _set_share_size(self, pool_id, pool_name, share_name, share_size):
        command_line = ['fquota', 'create', pool_id, pool_name,
                        share_name, str(share_size) + 'G', '-t', 'folder']
        self._execute(command_line)

        LOG.debug('Set Share [%(share_name)s] '
                  'Size [%(share_size)s G] completed.', {
                      'share_id': share_name,
                      'share_size': share_size})
        return

    def _get_share_size(self, pool_id, pool_name, share_name):
        share_size = None
        command_line = ['fquota', 'status', pool_id,
                        pool_name, '-t', 'folder']
        rc, quota_status = self._execute(command_line)

        for share_quota in quota_status:
            if share_quota['name'] == share_name:
                share_size = round(bi_to_gi(int(share_quota['quota'])), 2)
                break

        return share_size

    def delete_share(self, share, share_server=None):
        pool_name = share_utils.extract_host(share['host'], level='pool')
        pool_id = self.pool_dict[pool_name]['id']

        if self._check_share_exist(pool_name, share['share_id']):
            command_line = ['folder', 'options', pool_id,
                            pool_name, '-d', share['share_id']]
            self._execute(command_line)
        else:
            LOG.warning('Share [%(share_id)s] is already deleted.', {
                'share_id': share['share_id']})

        LOG.info('Delete Share [%(share_id)s] completed.', {
            'share_id': share['share_id']})

    def _check_share_exist(self, pool_name, share_name):
        share_exist = False
        path = self.pool_dict[pool_name]['path']
        command_line = ['pagelist', 'folder', path]
        rc, subfolders = self._execute(command_line)
        for subfolder in subfolders:
            if subfolder['name'] == share_name:
                share_exist = True
        return share_exist

    def update_access(self, share, access_rules, add_rules,
                      delete_rules, share_server=None):
        if not (add_rules or delete_rules):
            self._clear_access(share, share_server)
            for access in access_rules:
                self.allow_access(share, access, share_server)
        else:
            for access in delete_rules:
                self.deny_access(share, access, share_server)
            for access in add_rules:
                self.allow_access(share, access, share_server)

    def _clear_access(self, share, share_server=None):
        pool_name = share_utils.extract_host(share['host'], level='pool')
        pool_path = self.pool_dict[pool_name]['path']
        share_path = pool_path + '/' + share['share_id']
        share_proto = share['share_proto'].lower()

        if share_proto == 'nfs':
            command_line = ['share', 'status', '-f', share_path]
            rc, nfs_status = self._execute(command_line)
            if nfs_status:
                host_list = nfs_status[0]['nfs_detail']['hostList']
                for host in host_list:
                    if host['host'] != '*':
                        command_line = ['share', 'options', share_path,
                                        'nfs', '-c', host['host']]
                        self._execute(command_line)

        elif share_proto == 'cifs':
            command_line = ['acl', 'get', share_path]
            rc, cifs_status = self._execute(command_line)
            for cifs_rule in cifs_status:
                if cifs_rule['type'] == 'user':
                    command_line = ['acl', 'set', share_path, '-u',
                                    cifs_rule['name'], '-a', 'd']
                    self._execute(command_line)

    def allow_access(self, share, access, share_server=None):
        pool_name = share_utils.extract_host(share['host'], level='pool')
        pool_path = self.pool_dict[pool_name]['path']
        share_path = pool_path + '/' + share['share_id']
        share_proto = share['share_proto'].lower()
        access_type = access['access_type']
        access_level = access['access_level']
        access_to = access['access_to']

        msg = self._check_access_legal(share_proto, access_type)
        if msg:
            raise exception.InvalidShareAccess(reason=_(msg))

        if share_proto == 'nfs':
            command_line = ['share', 'options', share_path, 'nfs',
                            '-h', access_to, '-p', access_level]
            self._execute(command_line)

        elif share_proto == 'cifs':
            if not self._check_user_exist(access_to):
                msg = _('Please create user [%(user)s] in advance.') % {
                    'user': access_to}
                LOG.error(msg)
                raise exception.InfortrendNASException(err=msg)

            if access_level == constants.ACCESS_LEVEL_RW:
                access_level = 'f'
            elif access_level == constants.ACCESS_LEVEL_RO:
                access_level = 'r'
            else:
                msg = _('Unsupported access_level: [%s].') % access_level
                raise exception.InvalidInput(msg)

            command_line = ['acl', 'set', share_path,
                            '-u', access_to, '-a', access_level]
            self._execute(command_line)

        LOG.info('Share [%(share_id)s] access to [%(access_to)s] '
                 'completed for protocol [%(share_proto)s]', {
                     'share_id': share['share_id'],
                     'access_to': access_to,
                     'share_proto': share_proto})

    def _ensure_protocol_on(self, share_path, share_proto, cifs_name):
        if not self._check_proto_enabled(share_path, share_proto):
            command_line = ['share', share_path, share_proto, 'on']
            if share_proto == 'cifs':
                command_line.extend(['-n', cifs_name])
            self._execute(command_line)

    def _check_proto_enabled(self, share_path, share_proto):
        command_line = ['share', 'status', '-f', share_path]
        rc, share_status = self._execute(command_line)
        if share_status:
            check_enabled = share_status[0][share_proto]
            if check_enabled:
                return True
        return False

    def _check_user_exist(self, user_name):
        command_line = ['useradmin', 'user', 'list']
        rc, user_list = self._execute(command_line)
        for user in user_list:
            if user['Name'] == user_name:
                return True
        return False

    def _check_access_legal(self, share_proto, access_type):
        msg = None
        if share_proto == 'cifs' and access_type != 'user':
            msg = 'Infortrend CIFS share can only access by USER.'
        elif share_proto == 'nfs' and access_type != 'ip':
            msg = 'Infortrend NFS share can only access by IP.'
        elif share_proto not in ('nfs', 'cifs'):
            msg = 'Unsupported protocol [%s].' % share_proto
        return msg

    def deny_access(self, share, access, share_server=None):
        pool_name = share_utils.extract_host(share['host'], level='pool')
        pool_path = self.pool_dict[pool_name]['path']
        share_path = pool_path + '/' + share['share_id']
        share_proto = share['share_proto'].lower()
        access_type = access['access_type']
        access_to = access['access_to']

        msg = self._check_access_legal(share_proto, access_type)
        if msg:
            LOG.warning(msg)
            return

        if share_proto == 'nfs':
            command_line = ['share', 'options', share_path,
                            'nfs', '-c', access_to]
            self._execute(command_line)

        elif share_proto == 'cifs':
            if not self._check_user_exist(access_to):
                LOG.warning('User [%(user)s] had been removed.', {
                    'user': access_to})
                return
            command_line = ['acl', 'set', share_path,
                            '-u', access_to, '-a', 'd']
            self._execute(command_line)

        LOG.info('Share [%(share_id)s] deny access [%(access_to)s] '
                 'completed for protocol [%(share_proto)s]', {
                     'share_id': share['share_id'],
                     'access_to': access_to,
                     'share_proto': share_proto})

    def get_pool(self, share):
        pool_name = share_utils.extract_host(share['host'], level='pool')
        if not pool_name:
            for pool in self.pool_dict.keys():
                if self._check_share_exist(pool, share['share_id']):
                    pool_name = pool
                    break
        return pool_name

    def ensure_share(self, share, share_server=None):
        share_proto = share['share_proto'].lower()
        pool_name = share_utils.extract_host(share['host'], level='pool')
        pool_path = self.pool_dict[pool_name]['path']
        return self._export_location(share, share_proto, pool_path)

    def extend_share(self, share, new_size, share_server=None):
        pool_name = share_utils.extract_host(share['host'], level='pool')
        pool_id = self.pool_dict[pool_name]['id']
        self._set_share_size(pool_id, pool_name, share['share_id'], new_size)

        LOG.info('Successfully Extend Share [%(share_id)s] '
                 'to size [%(new_size)s G].', {
                     'share_id': share['share_id'],
                     'new_size': new_size})

    def manage_existing(self, share, driver_options):
        share_proto = share['share_proto'].lower()
        pool_name = share_utils.extract_host(share['host'], level='pool')
        pool_id = self.pool_dict[pool_name]['id']
        pool_path = self.pool_dict[pool_name]['path']
        input_location = share['export_locations'][0]['path']
        display_name = share['display_name']

        ch_ip, share_name = self._parse_location(input_location, share_proto)

        if not self._check_channel_ip(ch_ip):
            msg = _('Export location ip: [%(ch_ip)s] '
                    'is incorrect, please use data port ip.') % {
                        'ch_ip': ch_ip}
            LOG.error(msg)
            raise exception.InfortrendNASException(err=msg)

        if not self._check_share_exist(pool_name, share_name):
            msg = _('Can not find Share [%(share_name)s] '
                    'in pool [%(pool_name)s].') % {
                        'share_name': share_name,
                        'pool_name': pool_name}
            LOG.error(msg)
            raise exception.InfortrendNASException(err=msg)

        share_path = pool_path + '/' + share_name
        self._ensure_protocol_on(share_path, share_proto, display_name)
        share_size = self._get_share_size(pool_id, pool_name, share_name)

        if not share_size:
            msg = _('Share [%(share_name)s] has no size limitation, '
                    'please set it first for Openstack management.') % {
                        'share_name': share_name}
            LOG.error(msg)
            raise exception.InfortrendNASException(err=msg)

        # rename share name
        command_line = ['folder', 'options', pool_id, pool_name,
                        '-e', share_name, share['share_id']]
        self._execute(command_line)

        location = self._export_location(share, share_proto, pool_path)

        LOG.info('Successfully Manage Infortrend Share [%(ift_name)s], '
                 'Size: [%(size)s G], Protocol: [%(share_proto)s], '
                 'Display name: [%(display_name)s].', {
                     'ift_name': share_name,
                     'size': share_size,
                     'share_proto': share_proto,
                     'display_name': display_name})

        return {'size': share_size, 'export_locations': location}

    def _parse_location(self, input_location, share_proto):
        ip = None
        ift_share_name = None
        if share_proto == 'nfs':
            location = input_location.split(':/')
            if len(location) == 2:
                ip = location[0]
                ift_share_name = location[1].split('/')[2]
        elif share_proto == 'cifs':
            location = input_location.split('\\')
            if (len(location) == 4 and
                    location[0] == "" and
                    location[1] == ""):
                ip = location[2]
                ift_share_name = location[3]

        if not (ip and ift_share_name):
            msg = _('Export location error, please check '
                    'ip: [%(ip)s], share_name: [%(share_name)s].') % {
                        'ip': ip,
                        'share_name': ift_share_name}
            LOG.error(msg)
            raise exception.InfortrendNASException(err=msg)

        return ip, ift_share_name

    def _check_channel_ip(self, channel_ip):
        channel_ip_exist = False
        for ch, ip in self.channel_dict.items():
            if ip == channel_ip:
                channel_ip_exist = True
                break
        return channel_ip_exist

    def unmanage(self, share):
        pool_name = share_utils.extract_host(share['host'], level='pool')
        pool_id = self.pool_dict[pool_name]['id']

        if not self._check_share_exist(pool_name, share['share_id']):
            LOG.warning('Share [%(share_name)s] does not exist.', {
                'share_name': share['share_id']})
            return

        unmanage_name = self.UNMANAGE_PREFIX % share['display_name']

        # rename share name
        command_line = ['folder', 'options', pool_id,
                        pool_name, '-e', share['share_id'], unmanage_name]
        self._execute(command_line)

        LOG.info('Successfully Unmanage Share [%(share_name)s], '
                 'and rename it to [%(new_name)s].', {
                     'share_name': share['share_id'],
                     'new_name': unmanage_name})

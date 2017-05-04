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

    def get_fake_service_status_nfs(self):
        return """(64175, 1234, 272, 0)

{"cliCode": [{"Return": "0x0000", "CLI": "Successful"}], "returnCode": [], "data": [{"A": {"NFS": {"displayName": "NFS", "state_time": "2017-05-04 14:19:53", "enabled": true, "cpu_rate": "0.0", "mem_rate": "0.0", "state": "exited", "type": "share"}}}]}


"""

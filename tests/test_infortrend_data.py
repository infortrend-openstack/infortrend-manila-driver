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


class InfortrendNASTestData():

    fake_service_status_nfs = """
{"cliCode": [{"Return": "0x0000", "CLI": "Successful"}],
 "returnCode": [],
 "data":
 [{"A":
 {"NFS":
 {"displayName": "NFS",
 "state_time": "2017-05-04 14:19:53",
 "enabled": false,
 "cpu_rate": "0.0",
 "mem_rate": "0.0",
 "state": "exited",
 "type": "share"}}}]}
""".replace('\n', '')

    fake_fquota_status_pool_01 = """
{"cliCode": [{"Return": "0x0000", "CLI": "Successful"}],
 "returnCode": [],
 "data":
 [{"used": "0",
 "type": "subfolder",
 "id": "805306560",
 "name": "manila-unmanage-01",
 "quota": "10737418240"},
 {"used": "0",
 "type": "subfolder",
 "id": "69",
 "name": "3bf7b448-514e-41f4-ae28-1a39a320b465",
 "quota": "12884901888"},
 {"used": "0",
 "type": "subfolder",
 "id": "268435521",
 "name": "47fb61f9-5831-4bb7-8717-aa88a2ddbd93",
 "quota": "53687091200"}]}
""".replace('\n', '')


    fake_folder_status = """
{"cliCode": [{"Return": "0x0000", "CLI": "Successful"}],
 "returnCode": [],
 "data":
 [{"utility": "1.00",
 "used": "33873920",
 "subshare": true,
 "share": false,
 "worm": "",
 "free": "321931386880",
 "fsType": "xfs",
 "owner": "A",
 "readOnly": false,
 "modifyTime": "2017-04-25 18:01",
 "directory": "/LV-1/share-pool-01",
 "volumeId": "6541BAFB2E6C57B6",
 "mounted": true,
 "size": "321965260800"},
 {"utility": "1.00",
 "used": "33812480",
 "subshare": true,
 "share": false,
 "worm": "",
 "free": "107287941120",
 "fsType": "xfs",
 "owner": "A",
 "readOnly": false,
 "modifyTime": "2017-03-17 16:59",
 "directory": "/LV-1/share-pool-02",
 "volumeId": "147A8FB67DA39914",
 "mounted": true,
 "size": "107321753600"}]}
""".replace('\n', '')

    fake_ifconfig_inet_one_ch = """
{"cliCode": [{"Return": "0x0000", "CLI": "Successful"}],
 "returnCode": [],
 "data":
 [{"datalink": "mgmt0",
 "status": "UP",
 "typeConfig": "DHCP",
 "IP": "172.27.112.125",
 "MAC": "00:d0:23:00:15:a6",
 "netmask": "255.255.240.0",
 "type": "dhcp",
 "gateway": "172.27.127.254"},
 {"datalink": "CH0",
 "status": "UP",
 "typeConfig": "DHCP",
 "IP": "172.27.112.223",
 "MAC": "00:d0:23:80:15:a6",
 "netmask": "255.255.240.0",
 "type": "dhcp",
 "gateway": "172.27.127.254"},
 {"datalink": "CH1",
 "status": "DOWN",
 "typeConfig": "DHCP",
 "IP": "",
 "MAC": "00:d0:23:40:15:a6",
 "netmask": "",
 "type": "",
 "gateway": ""},
 {"datalink": "CH2",
 "status": "DOWN",
 "typeConfig": "DHCP",
 "IP": "",
 "MAC": "00:d0:23:c0:15:a6",
 "netmask": "",
 "type": "",
 "gateway": ""},
 {"datalink": "CH3",
 "status": "DOWN",
 "typeConfig": "DHCP",
 "IP": "",
 "MAC": "00:d0:23:20:15:a6",
 "netmask": "",
 "type": "",
 "gateway": ""}]}
""".replace('\n', '')


    fake_ifconfig_inet_two_ch = """
{"cliCode": [{"Return": "0x0000", "CLI": "Successful"}],
 "returnCode": [],
 "data":
 [{"datalink": "mgmt0",
 "status": "UP",
 "typeConfig": "DHCP",
 "IP": "172.27.112.125",
 "MAC": "00:d0:23:00:15:a6",
 "netmask": "255.255.240.0",
 "type": "dhcp",
 "gateway": "172.27.127.254"},
 {"datalink": "CH0",
 "status": "UP",
 "typeConfig": "DHCP",
 "IP": "172.27.112.223",
 "MAC": "00:d0:23:80:15:a6",
 "netmask": "255.255.240.0",
 "type": "dhcp",
 "gateway": "172.27.127.254"},
 {"datalink": "CH1",
 "status": "UP",
 "typeConfig": "DHCP",
 "IP": "172.27.113.209",
 "MAC": "00:d0:23:40:15:a6",
 "netmask": "255.255.240.0",
 "type": "dhcp",
 "gateway": "172.27.127.254"},
 {"datalink": "CH2",
 "status": "DOWN",
 "typeConfig": "DHCP",
 "IP": "",
 "MAC": "00:d0:23:c0:15:a6",
 "netmask": "",
 "type": "",
 "gateway": ""},
 {"datalink": "CH3",
 "status": "DOWN",
 "typeConfig": "DHCP",
 "IP": "",
 "MAC": "00:d0:23:20:15:a6",
 "netmask": "",
 "type": "",
 "gateway": ""}]}
""".replace('\n', '')

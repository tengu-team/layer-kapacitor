#!/usr/bin/python3
# Copyright (C) 2017  Qrama
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import subprocess

import charmhelpers.fetch.archiveurl
from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set, open_port, unit_private_ip, close_port, config
from charmhelpers.core.templating import render
from charmhelpers.core.host import service_restart


@when_not('layer-kapacitor.installed')
def install_layer_kapacitor():
    kapacitor_dir = '/opt/kapacitor'
    if not os.path.isdir(kapacitor_dir):
        os.mkdir(kapacitor_dir)
    handler = charmhelpers.fetch.archiveurl.ArchiveUrlFetchHandler()
    handler.download('https://dl.influxdata.com/kapacitor/releases/kapacitor_1.3.1_amd64.deb',
                     kapacitor_dir + '/kapacitor_1.3.1_amd64.deb')
    subprocess.check_call(['sudo', 'dpkg', '-i', '/opt/kapacitor/kapacitor_1.3.1_amd64.deb'])
    set_state('layer-kapacitor.installed')
    status_set('blocked', 'Waiting for relation with InfluxDB.')


@when('layer-kapacitor.installed', 'influxdb.available')
@when_not('layer-kapacitor.connected')
def connect_kapacitor(influxdb):
    status_set('waiting', 'Kapacitor connected to InfluxDB.')
    print("influxdb reachable at http://{}:{}".format(influxdb.hostname(), influxdb.port()))
    conf = config()
    port = conf['port']
    render(source='kapacitor.conf',
           target='/etc/kapacitor/kapacitor.conf',
           context={
               'port': str(port),
               'influxdb': influxdb,
               'hostname': unit_private_ip()
           })
    set_state('layer-kapacitor.connected')


@when('layer-kapacitor.connected')
@when_not('layer-kapacitor.started')
def start_kapacitor():
    conf = config()
    port = conf['port']
    open_port(port)
    subprocess.check_call(['sudo', 'service', 'kapacitor', 'start'])
    status_set('active', '(Ready) Kapacitor started.')
    set_state('layer-kapacitor.started')


@when('layer-kapacitor.started', 'config.changed', 'influxdb.available')
def change_configuration(influxdb):
    status_set('maintenance', 'configuring Kapacitor')
    conf = config()
    port = conf['port']
    old_port = conf.previous('port')
    if conf.changed('port'):
        render(source='kapacitor.conf',
               target='/etc/kapacitor/kapacitor.conf',
               context={
                   'port': str(port),
                   'influxdb': influxdb,
                   'hostname': unit_private_ip()
               })
        if old_port is not None:
            close_port(old_port)
        open_port(port)
        service_restart("kapacitor")
    status_set('active', '(Ready) Kapacitor started.')

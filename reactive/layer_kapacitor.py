# !/usr/bin/python3
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
# pylint: disable=c0111,c0103,c0301,c0412,e0401

import os
import subprocess

import charmhelpers.fetch.archiveurl
from charms.reactive import when, when_not, set_flag, clear_flag
from charmhelpers.core.hookenv import status_set, config, open_port, close_port, unit_private_ip
from charmhelpers.core.templating import render
from charmhelpers.core.host import service_start, service_restart, service_stop


@when_not('kapacitor.installed')
def install_kapacitor():
    kapacitor_dir = '/opt/kapacitor'
    if not os.path.isdir(kapacitor_dir):
        os.mkdir(kapacitor_dir)
    handler = charmhelpers.fetch.archiveurl.ArchiveUrlFetchHandler()
    handler.download('https://dl.influxdata.com/kapacitor/releases/kapacitor_1.3.1_amd64.deb',
                     kapacitor_dir + '/kapacitor_1.3.1_amd64.deb')
    subprocess.check_call(['sudo', 'dpkg', '-i', '/opt/kapacitor/kapacitor_1.3.1_amd64.deb'])
    status_set('blocked', 'Waiting for relation with InfluxDB')
    set_flag('kapacitor.installed')


@when('kapacitor.installed', 'influxdb.available')
@when_not('kapacitor.connected')
def connect_kapacitor(influxdb):
    status_set('maintenance', 'Connecting Kapacitor to InfluxDB')
    port = config()['port']
    render(source='kapacitor.conf',
           target='/etc/kapacitor/kapacitor.conf',
           context={
               'port': str(port),
               'influxdb': influxdb,
               'hostname': unit_private_ip()
           })
    set_flag('kapacitor.connected')


@when('kapacitor.connected')
@when_not('kapacitor.started')
def start_kapacitor():
    open_port(config()['port'])
    service_start('kapacitor')
    status_set('active', '(Ready) Kapacitor is running')
    set_flag('kapacitor.started')


@when('kapacitor.started', 'config.changed', 'influxdb.available')
def change_configuration(influxdb):
    status_set('maintenance', 'Configuring Kapacitor')
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
        service_restart('kapacitor')
    status_set('active', '(Ready) Kapacitor is running')


@when('kapacitor.started')
@when_not('influxdb.available')
def relation_removed():
    clear_flag('kapacitor.connected')
    clear_flag('kapacitor.started')
    service_stop('kapacitor')
    close_port(config()['port'])
    status_set('blocked', 'Waiting for relation with InfluxDB.')


@when('kapacitor.started', 'kapacitor.available')
def configure_relation(kapacitor):
    kapacitor.configure(unit_private_ip(), config()['port'])

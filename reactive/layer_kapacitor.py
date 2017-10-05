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
    handler.download('https://dl.influxdata.com/kapacitor/releases/kapacitor_1.3.1_amd64.deb', kapacitor_dir + '/kapacitor_1.3.1_amd64.deb')
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
           target='/usr/local/etc/kapacitor.conf',
           context={
               'port': str(port),
               'influxdb': influxdb,
               'hostname': unit_private_ip()
           })

    set_state('layer-kapacitor.connected')

@when('layer-kapacitor.connected')
@when_not('layer-kapacitor.started')
def start_kapacitor():
    open_port(9092)
    subprocess.check_call(['sudo', 'service', 'kapacitor', 'start'])
    set_state('layer-kapacitor.started')
    status_set('active', '(Ready) Kapacitor started.')

@when('layer-kapacitor.started', 'config.changed', 'influxdb.available')
def change_configuration(influxdb):
    conf = config()
    port = conf['port']
    old_port = conf.previous('port')
    if conf.changed('port'):
        render(source='kapacitor.conf',
               target='/usr/local/etc/kapacitor.conf',
               context={
                   'port': str(port),
                   'influxdb': influxdb,
                   'hostname': unit_private_ip()
               })
        if old_port is not None:
           close_port(old_port)
        open_port(port)
        service_restart("kapacitor")
        

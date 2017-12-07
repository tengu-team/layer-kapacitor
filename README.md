# Overview

Kapacitor is a data processing engine.  It can process both stream and batch
data from InfluxDB. This charm installs [Kapacitor](https://docs.influxdata.com/kapacitor)
and connect it to a running times series database.

# Usage

Deploy the Kapacitor charm and the required influxDB charm and add the relation between the two charms:

```bash
juju deploy cs:~tengu-team/kapacitor-0
juju deploy cs:~chris.macnaughton/influxdb-7
juju add-relation kapacitor influxdb
```
Kapacitor is providing [a custom interface](https://github.com/tengu-team/interface-kapacitor).


# Contact Information

## Bugs

Report bugs in the [layer-kapacitor GitHub repo](https://github.com/tengu-team/layer-kapacitor/issues).

## Authors

 - Dixan Peña Peña <dixan.pena@tengu.io>

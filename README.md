# Overview

Kapacitor is a data processing engine.  It can process both stream and batch
data from InfluxDB. This charm installs [Kapacitor](https://docs.influxdata.com/kapacitor)
and connect it to a running InfluxDB database.

# Usage

Deploy the Kapacitor charm and the required InfluxDB charm and add the relation between the two charms:

```bash
juju deploy kapacitor
juju deploy cs:~chris.macnaughton/influxdb-7
juju add-relation kapacitor influxdb
```
Kapacitor provides [a custom interface](https://github.com/tengu-team/interface-kapacitor).

# Contact Information

## Bugs

Report bugs in the [layer-kapacitor GitHub repo](https://github.com/tengu-team/layer-kapacitor/issues).

## Authors

 - Michiel Ghyselinck <michiel.ghyselinck@tengu.io>
 - Sébastien Pattyn <sebastien.pattyn@tengu.io>
 - Dixan Peña Peña <dixan.pena@tengu.io>

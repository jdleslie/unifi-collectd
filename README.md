unifi-collectd
==============
This script outputs strings suitable for consumption by the collectd exec plugin

Example collectd.conf fragment is below:
* unifi-collectd installed in /opt/unifi-collectd
* Be sure collectd's standard types.db is referenced in the configuration
* Unifi controller hostname and interval for polling set by collectd environment variables

```
TypesDB "/opt/unifi-collectd/types.db"
LoadPlugin exec
<Plugin "exec">
        Exec "daemon:daemon" "/opt/unifi-collectd/unifi_collectd.sh"
</Plugin>
```

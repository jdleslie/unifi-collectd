unifi-collectd
==============
This script outputs strings suitable for consumption by the collectd exec plugin

Example collectd.conf syntax
* unifi-collectd installed in /opt/unifi-collectd
* collectd libraries installed using Debian package locations
* controller hostname and interval for polling set by collectd environment variables

```
TypesDB "/opt/unifi-collectd/types.db"
LoadPlugin exec
<Plugin "exec">
        Exec "daemon:daemon" "/opt/unifi-collectd/unifi_collectd.sh"
</Plugin>
```

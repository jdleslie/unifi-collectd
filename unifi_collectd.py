#!/usr/bin/env python

import argparse, os, datetime, time, collections
from unifi.controller import Controller

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--interval', default=None,
                    help='seconds between polling requests, if not specified COLLECTD_INTERVAL is used, and 60 otherwise')
parser.add_argument('-c', '--controller', default=None,
                    help='the controller address, if not specified COLLECTD_HOSTNAME is used and "unifi" otherwise')
parser.add_argument('-u', '--username', default='ubnt',
                    help='the controller username (default "ubnt")')
parser.add_argument('-p', '--password', default='ubnt',
                    help='the controller password (default "ubnt")')
parser.add_argument('-v', '--version', default='v2',
                    help='the controller base version (default "v2")')
parser.add_argument('-s', '--site_id', default='default',
                    help='the site ID, UniFi >=3.x only (default "default")')
parser.add_argument('-P', '--port', default=8443, 
                    help='the port on the unifi controller for the API. Default to 8443.')
args = parser.parse_args()

if not args.interval:
    args.interval = float(os.getenv('COLLECTD_INTERVAL', 60))
args.interval = int(args.interval)
if not args.controller:
    args.controller = os.getenv('COLLECTD_HOSTNAME', 'unifi')

now = None
controller = None

def putval(identifier, values):
    values = isinstance(values, collections.Iterable) and values or [values]
    kwargs = {
        'identifier': identifier,
        'interval': args.interval,
        'now': now.strftime("%s"),
        'values': ':'.join(map(str, values)),
    }
    print "PUTVAL {identifier} interval={interval} {now}:{values}".format(**kwargs)

def hostname(ap):
    return ap['name'].split()[0]

def clean_ssid(ssid):
    return ssid.replace(' ', '_').replace('-', '_')

def print_controller_stats(c):
    clients = c.get_clients()
    putval(c.host + '/unifi_num_sta/ath_nodes', len(clients) )
    clients_radio = collections.Counter(map(lambda x: str(x['radio']), c.get_clients()) )
    putval(c.host + '/unifi_num_sta/num_sta', (clients_radio['ng'], clients_radio['na']) )

def print_ap_stats(ap):
    putval(hostname(ap) + '/unifi_num_sta/ath_nodes', (ap['ng-num_sta'], ap['na-num_sta']) )
    putval(hostname(ap) + '/unifi_num_sta/num_sta', (ap['ng-num_sta'], ap['na-num_sta']) )

def print_essid_stats(ap):
    for vap in ap['vap_table']:
        assert not '/' in vap['essid']
        kwargs = {
            'host': hostname(ap),
            'essid': clean_ssid(vap['essid']),
            'radio': vap['radio'],
        }
        identifier = lambda type: "{host}/unifi_essid_{essid}-{radio}/{}".format(type, **kwargs)
        values = lambda *args: [vap[x] for x in args]

        # Symmetrical interface stats
        prefixes = ['if_', 'rx_', 'tx_']
        bases = ['bytes', 'packets', 'dropped', 'errors']
        for type, rx, tx in [ [p + b for p in prefixes] for b in bases]:
            type = type == 'if_bytes' and 'if_octets' or type
            putval(identifier(type), values(rx, tx) )

        # Copy of Unifi -> Access Points -> Performance bar charts (TX 2G/5G)
        putval(identifier('tx_performance'), values('tx_dropped', 'tx_retries', 'tx_packets') )

        # Clients associated with ESSID on this AP
        putval(identifier('ath_nodes'), values('num_sta'))

        # Miscellaneous statistics
        prefixes = ['ath_stat-', '']
        bases = ['ccq', 'rx_frags', 'rx_nwids', 'rx_crypts']
        for type, key in [ [p + b for p in prefixes] for b in bases]:
            putval(identifier(type), values(key) )

if __name__ == '__main__':
    from urllib2 import URLError, HTTPError

    while True:
        now = datetime.datetime.utcnow()

        try:
            if not controller: 
                controller = Controller(args.controller, args.username, args.password, args.port, args.version, args.site_id)
#                controller = Controller(**args)
            for ap in controller.get_aps():
                print_controller_stats(controller)
                print_ap_stats(ap)
                print_essid_stats(ap)

            time.sleep(args.interval)            
        except (URLError, HTTPError) as err:
            controller = None
            time.sleep(10)
            continue
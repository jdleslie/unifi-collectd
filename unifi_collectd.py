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
parser.add_argument('-s', '--siteid', default='default',
                    help='the site ID, UniFi >=3.x only (default "default")')
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

def print_ap_stats(ap):
    prefix = hostname(ap) + '/unifi_ap'
    putval(prefix + '/scanning', ap['scanning'] and 1 or 0)
    putval(prefix + '/num_sta-na', ap['ng-num_sta'])
    putval(prefix + '/num_sta-ng', ap['na-num_sta'])

def print_essid_stats(ap):
    elements = ['num_sta', 'ccq', 'tx_retries', 'rx_frags', 'rx_nwids', 'rx_crypts']
    prefixes = ['tx', 'rx']
    bases = ['bytes', 'packets', 'dropped', 'errors']
    elements += [prefix + '_' + base for base in bases for prefix in prefixes]

    for vap in ap['vap_table']:
        assert not '/' in vap['essid']
        kwargs = {
            'host': hostname(ap),
            'essid': vap['essid'],
            'radio': vap['radio'],
        }
        identifier = lambda m: "{host}/unifi_essid-{essid}/{}-{radio}".format(m, **kwargs)

        for key, value in vap.iteritems():
            if key in elements:
                putval(identifier(key), value)

while True:
    now = datetime.datetime.utcnow()

    try:
        controller = Controller(args.controller, args.username, args.password, args.version, args.siteid)
    except:
        time.sleep(5)
        continue
    else:
        for ap in controller.get_aps():
            print_ap_stats(ap)
            print_essid_stats(ap)
        time.sleep(args.interval)
    

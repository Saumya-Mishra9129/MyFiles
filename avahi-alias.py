#! /usr/bin/env python2
'''
Register a mDNS/DNS-SD alias name for your computer using the Avahi daemon
This script will register an alternate CNAME alias besides your hostname,
which could be useful for ex. when serving several http virtual hosts on
the local network.
Why a CNAME? You could also publish your current address with avahi-publish-address
but on a multihomed host (connected via wifi0 and eth0 perhaps) a single
address will not be valid on both networks. So this publishes a CNAME to your
hostname, which, by default, is already published by Avahi.
domain should almost always be .local
the cname is not restricted to ascii, it'll be encoded as IDNA
The alias will stay published until the script runs.
'''
import avahi, dbus
from encodings.idna import ToASCII

# Got these from /usr/include/avahi-common/defs.h
CLASS_IN = 0x01
TYPE_CNAME = 0x05

TTL = 60

def publish_cname(cname):
    bus = dbus.SystemBus()
    server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
            avahi.DBUS_INTERFACE_SERVER)
    group = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.EntryGroupNew()),
            avahi.DBUS_INTERFACE_ENTRY_GROUP)

    if not '.' in cname:
        cname = cname + '.local'
    rdata = avahi.string_to_byte_array(createRR(server.GetHostNameFqdn()))
    cname = encode_dns(cname)

    group.AddRecord(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, dbus.UInt32(0),
        cname, CLASS_IN, TYPE_CNAME, TTL, rdata)
    group.Commit()


def encode_dns(name):
    return '.'.join( ToASCII(p) for p in name.split('.') if p )

def createRR(name):
    out = []
    for part in name.split('.'):
        if part == '': continue
        out.append(chr(len(part)))
        out.append(ToASCII(part))
    out.append('\0')
    return ''.join(out)

if __name__ == '__main__':
    import time, sys, locale
    if len(sys.argv)<2:
        print("Usage: %s hostname.local [hostname2.local] [hostname3.local]" % sys.argv[0])
        sys.exit(-1)

    for each in sys.argv[1:]:
        name = str(each, locale.getpreferredencoding())
        publish_cname(name)
    try:
        while 1: time.sleep(60)
    except KeyboardInterrupt:
        print("Exiting")


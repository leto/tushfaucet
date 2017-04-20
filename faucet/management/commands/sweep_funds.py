from django.core.management.base import BaseCommand, CommandError
from pyZcash.rpc.ZDaemon import *

# Sweep coinbase funds into zaddr. Not sure where to put this
zd = ZDaemon()
zaddrs = zd.z_listaddresses()
zd.sweep_coinbase(zaddrs[0])

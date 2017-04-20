from django.core.management.base import BaseCommand, CommandError
from pyZcash.rpc.ZDaemon import *

class Command(BaseCommand):
	help = 'Sweeps coinbase rewards into first zaddr'

	def handle(self, *args, **options):
		zd = ZDaemon()
		zaddrs = zd.z_listaddresses()
		zd.sweep_coinbase(zaddrs[0])

from django.core.management.base import BaseCommand, CommandError
from faucet.models import HealthCheck
from pyZcash.rpc.ZDaemon import *

class Command(BaseCommand):
	help = 'Updates health values shown on main page'

	def handle(self, *args, **options):
		zd = ZDaemon()
		balance = zd.getbalance()
		height = zd.getNetworkHeight()
		difficulty = zd.getNetworkDifficulty()

		# Sweep coinbase funds into zaddr. Not sure where to put this
		zaddrs = zd.z_listaddresses()
		zd.sweep_coinbase(zaddrs[0])

		hc = HealthCheck()
		hc.balance = balance
		hc.height = height
		hc.difficulty = difficulty
		hc.save()

from django.core.management.base import BaseCommand, CommandError
from faucet.models import HealthCheck
from pyZcash.rpc.ZDaemon import *

class Command(BaseCommand):
	help = 'Updates blockchain health values shown on main page'

	def handle(self, *args, **options):
		zd = ZDaemon()
		# balance = zd.getsbalance()
		t_balance = zd.z_gettotalbalance()['transparent']
		z_balance = zd.z_gettotalbalance()['private']
		height = zd.getNetworkHeight()
		difficulty = zd.getNetworkDifficulty()

		hc = HealthCheck()
		hc.t_balance = t_balance
		hc.z_balance = z_balance
		hc.height = height
		hc.difficulty = difficulty
		hc.save()

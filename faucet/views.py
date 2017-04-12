from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone

from datetime import *

from pyZcash.rpc.ZDaemon import *
from faucet.models import *


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('HTTP_X_REAL_IP')
    return ip

def index(request):
	# TODO: Going to show the page no matter what, so pull these variables out.
	if HealthCheck.objects.latest('timestamp'):
		hc = HealthCheck.objects.latest('timestamp')
		balance = hc.balance
		difficulty = hc.difficulty
		height = hc.height
		payouts = Drip.objects.count()
	else:
		balance = '0'
		difficulty = '0'
		height = '0'
	#TODO: where to put this?
	zd = ZDaemon()
	version = zd.getVersion()

	#If it is a post, an address was submitted.
	if request.method == 'POST':
		# Check IP and payout address
		# This is the old workaround, added get_client_ip
		# ip = request.META.get('REMOTE_ADDR')
        # if ip == '127.0.0.1':
        #     ip = request.META.get('HTTP_X_REAL_IP')
		ip = get_client_ip(request)
		address = request.POST.get('address', '')
		print "IP: ", ip
		print "address: ", address
		try:
			last_payout = Drip.objects.filter(Q(ip=ip) | Q(address=address)).order_by('-timestamp')[0]
        		now = datetime.utcnow().replace(tzinfo=timezone.get_current_timezone())
			timesince = (now - last_payout.timestamp).total_seconds()

			# TODO: keep track of sessions as well, track one per session?

			if timesince < (60*60*12):
				return render(request, 'faucet/faucet.html', {'version':version,'balance':hc.balance,'difficulty':hc.difficulty,'height':hc.height, 'payouts':payouts, 'flash':True, 'message':"Sorry, you received a payout too recently.  Come back later."})

		except (Drip.DoesNotExist, IndexError) as e:
			# Nothing in queryset, so we've never seen this ip and address before (individually)
			pass

		# zd = ZDaemon()
		tx = zd.sendTransparent(address, 0.1)

		# TODO: Give better error if faucet is empty!

		#Did the tx work?
		if tx:
			#Save Drip.
			drip = Drip(address=address,txid=tx,ip=ip)
			drip.save()
			return render(request, 'faucet/faucet.html', {'version':version,'balance':balance,'difficulty':difficulty,'height':height, 'payouts':payouts, 'flash':True, 'message':"Sent! txid:" + tx})
		else:
			return render(request, 'faucet/faucet.html', {'version':version,'balance':balance,'difficulty':difficulty,'height':height, 'payouts':payouts, 'flash':True, 'message':"Issue sending transaction.  Is your address correct?"})


	return render(request, 'faucet/faucet.html', {'version':version,'balance':balance,'difficulty':difficulty,'height':height, 'payouts':payouts, 'flash':False, 'message':""})

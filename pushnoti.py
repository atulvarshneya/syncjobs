
import http.client, urllib

import config

def pushnotify(message):
	reg = config.Config("/shares/USBDRIVE/SYNCJOBS.conf/etc/registry").read_registry()
	APP_TOKEN = reg["app-token"]
	# print("APP_TOKEN",APP_TOKEN)
	USER_KEY = reg["user-key"]
	# print("USER_KEY",USER_KEY)

	conn = http.client.HTTPSConnection("api.pushover.net:443")
	conn.request("POST", "/1/messages.json",
  		urllib.parse.urlencode({
			"token": APP_TOKEN,
			"user": USER_KEY,
			"message": message,
			}),
		{ "Content-type": "application/x-www-form-urlencoded" })
	resp = conn.getresponse()
	# print(resp.status, resp.reason)
	return 0

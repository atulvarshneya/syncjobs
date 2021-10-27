
import http.client, urllib

import os
import syncjobs.config as config

def pushnotify(message, webui_url=None):
	regfile = os.environ.get("SJREGISTRY")
	if regfile is None:
		regfile = "~/.sjregistry"
	reg = config.Config(regfile).read_registry()
	APP_TOKEN = reg["app-token"]
	# print("APP_TOKEN",APP_TOKEN)
	USER_KEY = reg["user-key"]
	# print("USER_KEY",USER_KEY)

	conn = http.client.HTTPSConnection("api.pushover.net:443")
	msgcontent = { "token": APP_TOKEN, "user": USER_KEY, "message": message, }
	if not webui_url is None:
		msgcontent["url"] = webui_url
		msgcontent["url_title"] = "Browse logs"
	conn.request("POST", "/1/messages.json",
  		urllib.parse.urlencode(msgcontent),
		{ "Content-type": "application/x-www-form-urlencoded" })
	resp = conn.getresponse()
	# print(resp.status, resp.reason)
	return 0

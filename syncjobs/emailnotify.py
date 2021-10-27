#!/usr/bin/python3

import syncjobs.config as config
import smtplib
import os

class Emailer:
	def sendmail(self, subject, content):
		regfile = os.environ.get("SJREGISTRY")
		if regfile is None:
			regfile = "~/.sjregistry"
		reg = config.Config(regfile).read_registry()
		SMTP_SERVER = reg["smtp-server"]
		SMTP_PORT = reg["smtp-port"]
		GMAIL_USERNAME = reg["gmail-username"]
		GMAIL_PASSWORD = reg["gmail-password"]
		RECIPIENT = reg["recipient"]

		#Create Headers
		headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + RECIPIENT,
		   "MIME-Version: 1.0", "Content-Type: text/html"]
		headers = "\r\n".join(headers)

		#Connect to Gmail Server
		session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
		session.ehlo()
		session.starttls()
		session.ehlo()

		#Login to Gmail
		session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

		#Send Email & Exit
		session.sendmail(GMAIL_USERNAME, RECIPIENT, headers + "\r\n\r\n" + content)
		session.quit

def emailnotify(message, webui_url=None):
	sender = Emailer()
	emailSubject = "netdisk1 backup"
	sender.sendmail(emailSubject, message)  
	return 0


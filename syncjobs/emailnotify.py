#!/usr/bin/python3

import syncjobs.config as config
import smtplib
import os
import syncjobs.logger as logger

class Emailer:
	def __init__(self):
		pass

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
	try:
		sender = Emailer()
		emailSubject = "netdisk1 backup"
		emailtxt = message + "\n\n" + webui_url
		sender.sendmail(emailSubject, emailtxt)  
	except smtplib.SMTPException as e:
		error_code = e.smtp_code
		error_message = e.smtp_error
		logger.log(2,error_message)


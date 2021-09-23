import os

class flaskconfig(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'just some random key'

#!/usr/bin/env python2

import json
import urllib2

api_key = "***************"
reg_ids = {} 
reg_ids['stian'] = '**********'
reg_ids['pelle'] = 'fkldjahs_lkjfdkjfhdaksjhfgdksjhgafkdsajhgfdkhgsakdh'
class gcm_server(object):

	def __init__(self, api_key, reg_ids):
		self.api_key = api_key
		self.reg_ids = reg_ids
		self.gcm_url = "https://android.googleapis.com/gcm/send"

	def send_data(self, to, data_content):
		reg_id_list = []
		for name in to:
			if name in self.reg_ids:
				key = self.reg_ids[name]
				reg_id_list.append(key)
	
		data = {
			'registration_ids' : reg_id_list,
			'data' : data_content
		}
	
		headers = {
			'Content-Type' : 'application/json',
			'Authorization' : 'key=' + self.api_key
		}
	
		request = urllib2.Request(self.gcm_url, json.dumps(data), headers)
		try:
			response = urllib2.urlopen(request)
			data = json.loads(response.read())
			print "Data:"
			print data
			return (True, 200, data)
		except urllib2.HTTPError as e:
			# read http://developer.android.com/google/gcm/gcm.html#response
			return (False, e.code, e.reason)

	def check_result(self, data):
		if data['failure'] == 0 and data['canonical_ids'] == 0:
			return True
		return False

	def handle_failed_result(self, to, data):
		to_index = 0
		for result in data['results']:
			if 'message_id' in result:
				if 'registration_id' in result:
					self.reg_ids[to[to_index]] = result['registration_id']
			else:
				error = result['error']
				if error == "MissingRegistration":
					#handle error in 'to' list
					pass
				if error == "InvalidRegistration":
					#handle reg_id formatting error 
					pass
				if error == "MismatchSenderId":
					#handle wrong sender error
					pass
				if error == "NotRegistered":
					#handle error by removing regi_id
					pass
				if error == "MessageTooBig":
					#handle error
					pass
				if error == "InvalidDataKey":
					#handle key error in data structure
					pass
				if error == "InvalidTtl":
					#handle error
					pass
				if error == "Unavailable":
					#handle timeout error
					#read http://developer.android.com/google/gcm/gcm.html#error_codes
					pass
				if error == "InternalServerError":
					#handle error
					#read http://developer.android.com/google/gcm/gcm.html#error_codes
					pass

data = {}
data["ball"] = "teste leke bille kose"
data["kos"] = 34

to = ['stian', 'pelle']

server = gcm_server(api_key, reg_ids)
result, status, data = server.send_data(to, data)
if result:
	if not server.check_result(data):
		server.handle_failed_result(to, data)
		print "Errors handled..."
	else:
		print "All ok"
else:
	print "Error: " + str(data)

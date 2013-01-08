import urllib2
import json

class Server(object):

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
    

class User(object):
    
    def __init__(self):
        self.user_id = None
        self.username = None
        self.password = None
        self.token = None
        self.reg_id = None

    def setValues(self, user_id, username, password, token, reg_id):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.token = token
        self.reg_id = reg_id    

class UserDatabase(object):
    
    def __init__(self):
        self.users_by_name = {}
        self.users_by_id = {}
        self.next_id = 0

    def add(self, username, password, token, reg_id):
        new_user = User()
        new_user.setValues(self.next_id, username, password, token, reg_id)
        self.users_by_id[self.next_id] = new_user
        self.users_by_name[username] = new_user
        self.next_id += 1
    
    def rem(self, user):
        user_id = user.user_id
        username = user.username
        del(self.users_by_id[user_id])
        del(self.users_by_name[username])
    
    def load(self):
        pass
    
    def save(self):
        return json.dumps(self.users_by_id)
    
    def list(self):
        print "Users:"
        print "%s\t| %-30s\t\t| %s" % ("UserID", "Username", "Register ID")
        print "-" * 100
        for user_id in self._user_ids():
            user = self.users_by_id[user_id]
            print "%s\t| %-30s\t\t| %s" % (user.user_id, user.username, user.reg_id)
    
    def _user_names(self):
        return self.users_by_name.keys()
    
    def _user_ids(self):
        return self.users_by_id.keys();
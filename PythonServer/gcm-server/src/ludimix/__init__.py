import urllib2
import json

class Server(object):

    def __init__(self, api_key, user_db):
        self.api_key = api_key
        self.user_db = user_db
        self.user_db.load()
        self.gcm_url = "https://android.googleapis.com/gcm/send"

    def send_data(self, to, data_content):
        ret = {}
        ret["reg_id_list"] = []
        ret["user_list"] = []
        for name in to:
            user = self.user_db.find_by_name(name)
            if not user == None:
                key = user.reg_ids # TODO: CHECK THIS
                if key == None or key == "":
                    continue
                ret["reg_id_list"].append(key)
                ret["user_list"].append(user)
        
        if len(ret["reg_id_list"]) < 1:
            ret["error"] = True
            ret["status_code"] = 0
            ret["error_reason"] = "NoRecipients"
            return ret
        
        data = {
            'registration_ids' : ret["reg_id_list"],
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
            ret["error"] = False
            ret["status_code"] = 200
            ret["data"] = data
            return ret
        except urllib2.HTTPError as e:
            # read http://developer.android.com/google/gcm/gcm.html#response
            ret["error"] = True
            ret["status_code"] = e.code
            ret["error_reason"] = e.reason
            return ret

    def check_result(self, result):
        if result["data"]['failure'] == 0 and result["data"]['canonical_ids'] == 0:
            return True
        return False

    def handle_failed_result(self, result):
        to = result["reg_id_list"]
        users = result["user_list"]
        data = result["data"]
        to_index = 0
        for result in data['results']:
            if 'message_id' in result:
                if 'registration_id' in result:
                    self.reg_ids[to[to_index]] = result['registration_id'] # TODO: Check this
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
        self.tokens = None
        self.reg_ids = None

    def setValues(self, user_id, username, password, tokens, reg_ids):
        self.user_id = int(user_id)
        self.username = username
        self.password = password
        self.tokens = tokens
        self.reg_ids = reg_ids
        
    def toString(self):
        string = {}
        string["user_id"] = self.user_id
        string["username"] = self.username
        string["password"] = self.password
        string["tokens"] = self.tokens
        string["reg_ids"] = self.reg_ids
        return json.dumps(string)
    
    def fromString(self, json_str):
        string = json.loads(json_str)
        self.user_id = int(string["user_id"]) 
        self.username = string["username"]
        self.password = string["password"] 
        self.tokens = string["tokens"]
        self.reg_ids = string["reg_ids"]
        
    def show(self):
        print "User ID:\t\t%s" % self.user_id 
        print "Username:\t\t%s" % self.username
        print "Password:\t\t%s" % self.password
        
        if not len(self.tokens) == 0:
            print "" 
        p = "Security tokens" 
        if len(self.tokens) == 0:
            p += ": \t-"
        else:
            p += " (excl. ''):"
            for token in self.tokens:
                p += "\n* '" + token + "'"
        print p
        
        if not len(self.reg_ids) == 0:
            print "" 
        p = "Register IDs" 
        if len(self.reg_ids) == 0:
            p += ": \t-"
        else:
            p += " (excl. ''):"
            for reg_id in self.reg_ids:
                p += "\n* '" + reg_id + "'"
            p += "\n"
        print p        

class UserDatabase(object):
    
    def __init__(self, path):
        self._users_by_name = {}
        self._users_by_id = {}
        self.next_id = 0
        self.path = path
        self.file = open(self.path, 'r+')

    def add(self, username, password, token, reg_ids):
        if not self.find_by_name(username) == None:
            return False
        new_user = User()
        new_user.setValues(self.next_id, username, password, token, reg_ids)
        self._users_by_id[self.next_id] = new_user
        self._users_by_name[username] = new_user
        self.next_id += 1
        return True
    
    def rem(self, user_id):
        user = self.find_by_id(user_id)
        if user == None:
            return False
        username = user.username
        del(self._users_by_id[user_id])
        del(self._users_by_name[username])
        return True
    
    def load(self):
        self._users_by_id = {}
        self._users_by_name = {}
        self.next_id = 0
        self.file.seek(0)
        read_data = self.file.readlines()
        for json_str in read_data:
            user = User()
            user.fromString(json_str)
            self._users_by_id[user.user_id] = user
            self._users_by_name[user.username] = user
            if user.user_id >= self.next_id:
                self.next_id = user.user_id + 1
    
    def save(self):
        save_data = ""
        for user_id in self._users_by_id:
            save_data += self._users_by_id[user_id].toString() + "\n"
            
        self.file.seek(0)        
        self.file.truncate()
        self.file.write(save_data)
    
    def list(self):
        print "Users:"
        print "%s\t| %-30s\t\t| %s" % ("UserID", "Username", "Registered")
        print "-" * 68
        for user_id in self._users_by_id:
            user = self._users_by_id[user_id]
            reg_id = "No" if len(user.reg_ids) == 0 else "Yes"
            print "%s\t| %-30s\t\t| %s" % (user.user_id, user.username, reg_id)
            
    def find_by_id(self, user_id):
        if not user_id in self._users_by_id:
            return None
        return self._users_by_id[user_id]        
        
    def find_by_name(self, username):
        if not username in self._users_by_name:
            return None
        return self._users_by_name[username]
    
    
    
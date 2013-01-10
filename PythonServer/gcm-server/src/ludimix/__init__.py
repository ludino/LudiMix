import hashlib
import json
import random
import select
import socket
import ssl
import string
import urllib2

class Connection(object):
    
    def __init__(self, newsocket, fromaddr, user_db):
        self.user_db = user_db
        self.connstream = ssl.wrap_socket(newsocket,
                                     server_side=True,
                                     certfile="key/server.crt",
                                     keyfile="key/server.key",
                                     ssl_version=ssl.PROTOCOL_TLSv1)
        print "New connection: " + str(self.connstream.fileno())
        self.connstream.send("service?")
        self.service = None
        self.user = None
            
    def get_pollable_object(self):
        return self.connstream
    
    """
    Errors:
    NotJson................Received data is not a valid json string
    NoCmdOrArgv............Received json object does not contain the keys 'cmd' AND 'argv'
    NotAuthenticated.......Client is not logged in, and command is not 'login'
    NoService..............Received service request is invalid
    MissingCredentials.....Received login request does not contain the key 
                           'username' AND 'password' within 'argv'
    WrongCredentials.......Received login request contains an invalid username or password
    Authenticated..........Received login request is accepted
    """
    def do_client(self, data):
        json_obj = None
        try:
            json_obj = json.loads(data)
        except:
            self.client_error("NotJson")
            return False
        
        command = None
        argv = None
        try:
            command = json_obj["cmd"]
            argv = json_obj["argv"]
        except:
            self.client_error("NoCmdOrArgv")
            return False
        
        #client not logged in
        if self.user == None:
            if command == "login":
                try:
                    username = argv["username"]
                    password = argv["password"]
                except:
                    self.client_error("MissingCredentials")
                    return False
                
                user = self.user_db.find_by_name(username)
                if user == None:
                    self.client_error("WrongCredentials")
                    return False
                elif not user.password == password:
                    self.client_error("WrongCredentials")
                    return False
                else:
                    self.connstream.write("Authenticated")
                    self.user = user
                    return True

            else:
                self.client_error("NotAuthenticated")
                return False
            
        #client already logged in
        else:
            self.connstream.write("Authorized command: " + command)
            return True

    
    def on_new_data(self):
        data = self.connstream.read().strip()
        if self.service == None:
            self.service = data
            if self.service == "client":
                self.connstream.write("OK ")
                return True
            else:
                self.client_error("NoService")
                return False
        elif self.service == "client":
            return self.do_client(data)
        else:
            self.server_error("on_new_data(): service != None, service != client")
            return False
        
    def server_error(self, error):
        self.connstream.write("InternalError")
        # TODO: log error
        
    def client_error(self, error):
        self.connstream.write(error)
        
    def close(self):
        print "Closing connection " + str(self.connstream.fileno())
        sock = self.connstream.unwrap()
        sock.close()
        
    def closed(self):
        print "Client disconnected " + str(self.connstream.fileno())

class Server(object):

    def __init__(self, api_key, user_db):
        self.api_key = api_key
        self.user_db = user_db
        self.user_db.load()
        self.gcm_url = "https://android.googleapis.com/gcm/send"

    def exit(self, reason=None):
        if reason == None:
            pass
        elif reason == "interrupt":
            print "Interupted..."
        print "\nExit exit exit"

    def run_daemon(self):
        bindsocket = socket.socket()
        bindsocket.bind(('127.0.0.1', 10023))
        bindsocket.listen(5)
        print "Running..."
        poll = select.poll()
        listen_fd = bindsocket.fileno()
        poll_mask = select.POLLIN | select.POLLPRI 
        poll.register(listen_fd, poll_mask)
        connections = {}
        while True:
            pollables = poll.poll()
            for pollable in pollables:
                fd, event = pollable
                if fd == listen_fd:
                    newsocket, fromaddr = bindsocket.accept()
                    new_connection = Connection(newsocket, fromaddr, self.user_db)
                    poll.register(new_connection.get_pollable_object(), poll_mask)
                    connections[newsocket.fileno()] = new_connection
                else:
                    print "New data on " + str(fd) + " " + str(event)
                    #print str((select.POLLIN, select.POLLPRI, select.POLLOUT, select.POLLERR, select.POLLHUP, select.POLLNVAL))
                    if event & select.POLLHUP > 0:
                        poll.unregister(fd)
                        connections[fd].closed()
                        del connections[fd]
                    elif event & select.POLLIN > 0:
                        status = connections[fd].on_new_data()
                        if status == False:
                            poll.unregister(fd)
                            connections[fd].close()
                            del connections[fd]

    def send_data(self, to, data_content):
        ret = {}
        ret["reg_id_list"] = []
        ret["user_list"] = []
        for name in to:
            user = self.user_db.find_by_name(name)
            if not user == None:
                keys = user.reg_ids
                if keys == None or keys == []:
                    continue
                for k in keys:
                    ret["reg_id_list"].append(k)
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
                    user = users[to_index]
                    index = user.tokens.index(to[to_index])
                    user.tokens[index] = result['registration_id']
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
        self.salt = None
        self.password_rounds = None
        self.tokens = None
        self.reg_ids = None


    """
    r1 = SHA512(msg + salt)
    r2 = SHA512(msg + salt + r1 + salt)
    r3 = SHA512(msg + salt + r1 + salt + r2 + salt)
    """
    @staticmethod
    def hash(msg):
        rounds = 100000
        random.seed()
        rand = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        m = hashlib.sha512()
        m.update(msg + rand)
        random.seed(m.hexdigest())
        salt_len = random.randrange(10, 20, 1)
        salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(salt_len))
        tmp = msg
        for _ in xrange(rounds):
            m = hashlib.sha512()
            m.update(tmp + salt)
            tmp = m.hexdigest()
        return tmp, salt, rounds

    def updatePassword(self, passwd, salt, rounds):
        self.password = passwd
        self.salt = salt
        self.password_rounds = rounds

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
        string["salt"] = self.salt
        string["password_rounds"] = self.password_rounds
        string["tokens"] = self.tokens
        string["reg_ids"] = self.reg_ids
        return json.dumps(string)
    
    def fromString(self, json_str):
        string = json.loads(json_str)
        self.user_id = int(string["user_id"]) 
        self.username = string["username"]
        self.password = string["password"] 
        self.salt = string["salt"]
        self.password_rounds = string["password_rounds"]
        self.tokens = string["tokens"]
        self.reg_ids = string["reg_ids"]
        
    def show(self):
        print "User ID:\t\t%s" % self.user_id 
        print "Username:\t\t%s" % self.username
        print "Password:\t\t%s" % ("-" if self.password == None else self.password)
        
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
        print "-" * 76
        print "| %s  | PW\t| %-30s\t\t| %s" % ("UserID", "Username", "Registered")
        print "-" * 76
        for user_id in self._users_by_id:
            user = self._users_by_id[user_id]
            pw = ("n" if user.password == None or user.password == "" else "Y")
            reg_id = ("No" if len(user.reg_ids) == 0 else "Yes")
            print "| %s\t  | %c\t| %-30s\t\t| %s" % (user.user_id, pw, user.username, reg_id)
        print "-" * 76
            
    def find_by_id(self, user_id):
        if not user_id in self._users_by_id:
            return None
        return self._users_by_id[user_id]        
        
    def find_by_name(self, username):
        if not username in self._users_by_name:
            return None
        return self._users_by_name[username]
    
    
    
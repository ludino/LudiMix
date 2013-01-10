#!/usr/bin/env python2

import json
import sys
import ludimix
import getpass
import sys

api_key = "AIzaSyDRHiFrhibsNqcAJwfb0jaFxv93GAgY-v0"
user_db_file = '/Volumes/macdata/Users/stianfauskanger/test/gcm-server/users'

def run_test(args):
    username = "stian"
    user_db = ludimix.UserDatabase(user_db_file)
    user_db.load()
    user = user_db.find_by_name(username)
    if user == None:
        print "User not found."
        run_listusers(args)
        exit()
    user.tokens.append("kjfhaslkjfhlsadjkhfsad")
    user.tokens.append("utyrweoyturtiuorytowri")
    user_db.save()
    
def run_daemon(args):
    user_db = ludimix.UserDatabase(user_db_file)
    user_db.load()
    server = ludimix.Server(api_key, user_db)
    try:
        server.run_daemon()
    except KeyboardInterrupt:
        server.exit("interrupt")
        sys.exit(0)
    

def run_cli(args):
    if len(args) < 2:
        syntax()

    user_db = ludimix.UserDatabase(user_db_file)
    user_db.load()    

    to = args[0]
    msg = " ".join(args[1:])
     
    data = {}
    data["msg"] = msg
    
    server = ludimix.Server(api_key, user_db)
    result = server.send_data([to], data)
    if result["error"]:
        print "Error: " + str(result["error_reason"])
    else:
        if not server.check_result(result):
            server.handle_failed_result(result)
            print "Errors handled..."
        else:
            print "All ok"

def run_listusers(args):
    user_db = ludimix.UserDatabase(user_db_file)
    user_db.load()    
    user_db.list()
    
def run_showuser(args):
    if len(args) < 1:
        syntax()
    username = args[0]
    user_db = ludimix.UserDatabase(user_db_file)
    user_db.load()
    user = user_db.find_by_name(username)
    if user == None:
        print "User not found."
        run_listusers(args)
        exit()
    user.show()    

def run_passwd(args):
    if len(args) < 1:
        syntax()
    username = args[0]
    passwd = getpass.getpass("Enter password:")
    passwd2 = getpass.getpass("Renter password:")
    if not passwd == passwd2:
        print "Passwords did not match"
        exit()

    user_db = ludimix.UserDatabase(user_db_file)
    user_db.load()
    user = user_db.find_by_name(username)
    passwdd, salt, rounds = ludimix.User.hash(passwd) # running for 0.333333 seconds on my computer
    
    user.updatePassword(passwdd, salt, rounds)
    user_db.save()
    print "Password set for '" + username + "'"

def run_adduser(args):
    if len(args) < 1:
        syntax()
    username = args[0]
    reg_ids = []
    if len(args) >= 2:
        reg_ids = [args[1]]
    
    user_db = ludimix.UserDatabase(user_db_file)
    user_db.load()
    if user_db.add(username, None, [], reg_ids):
        user_db.save()
        print "User '" + username + "' added"
        exit()
    print "User '" + username + "' already exists"

def run_remuser(args):
    if len(args) < 1:
        syntax()
    username = args[0]
    user_db = ludimix.UserDatabase(user_db_file)
    user_db.load()
    user = user_db.find_by_name(username)
    if user == None:
        print "User not found."
        run_listusers(args)
        exit()
    user_db.rem(user.user_id)
    user_db.save()
    print "User '" + username + "' removed" 

def syntax():
    print "Syntax:"
    print "gcm-server.py [option] [user] [msg|reg_id]"
    print "options:"
    print "\t--daemon\t\t\t\tRun as a daemon"
    print "\t--cli to msg\t\t\t\tSend msg to user once, and quit"
    print "\t--listusers\t\t\t\tList users"
    print "\t--showuser user\t\t\t\tShow information about user"
    print "\t--passwd user\t\t\t\tSet password for user"
    print "\t--adduser username [reg_id]\t\tAdd user"
    print "\t--remuser\t\t\t\tRemove users"
    exit()

def main():
    runAs = ""
    args = []
    if len(sys.argv) >= 2:
        runAs = sys.argv[1]
        args = sys.argv[2:]
    if runAs == "--daemon":
        run_daemon(args)
    elif runAs == "--cli":
        run_cli(args)
    elif runAs == "--listusers":
        run_listusers(args)
    elif runAs == "--showuser":
        run_showuser(args)
    elif runAs == "--passwd":
        run_passwd(args)
    elif runAs == "--adduser":
        run_adduser(args)
    elif runAs == "--remuser":
        run_remuser(args)
    elif runAs == "--test":
        run_test(args)
    else:
        syntax()

if __name__ == '__main__':
    main()
    
    
    
    
    
    
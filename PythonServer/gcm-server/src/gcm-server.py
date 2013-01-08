#!/usr/bin/env python2

import json
import urllib2
import sys
import ludimix

api_key = "AIzaSyDRHiFrhibsNqcAJwfb0jaFxv93GAgY-v0"
reg_ids = {} 
reg_ids['stian'] = 'APA91bHKF6_ACp20R3bZ3GF8_MYb_1icHWuTZ6Ja7UyyoW82P6Rr2gAo3qm-mEFjl3dQ2RLmMdGun0nI3jgnayNj96hrMbtBSyzh3Eve-bOA53F0JRUjXz8wHMT8EjT1RJxh1HvFs5m2qs92leuQUVAPxhppKKy3sQ'
reg_ids['pelle'] = 'fkldjahs_lkjfdkjfhdaksjhfgdksjhgafkdsajhgfdkhgsakdh'

def run_test(args):
    user_db = ludimix.UserDatabase()
    user_db.load()
    user_db.add("stian", "secret1", "fkdljashl", "dfjhsalk")
    user_db.add("thomas", "secret2", "kjhfdla", "fdadsfd")
    user_db.list()
    
    print user_db.save()

def run_daemon(args):
    pass

def run_cli(args):
    pass

def run_listusers(args):
    user_db = ludimix.UserDatabase()
    user_db.load()
    
    user_db.add("stian", "secret1", "fkdljashl", "dfjhsalk")
    user_db.add("thomas", "secret2", "kjhfdla", "fdadsfd")
    
    user_db.list()

def run_adduser(args):
    pass

def run_remuser(args):
    pass

def main(args):
    data = {}
    data["ball"] = "teste leke bille kose"
    data["kos"] = 34
    
    to = ['stian', 'pelle']
    
    server = ludimix.Server(api_key, reg_ids)
    result, status, data = server.send_data(to, data)
    if result:
        if not server.check_result(data):
            server.handle_failed_result(to, data)
            print "Errors handled..."
        else:
            print "All ok"
    else:
        print "Error: " + str(data)

def syntax():
    print "Syntax:"
    print "gcm-server.py [option] [user] [msg|password]"
    print "options:"
    print "\t--daemon\t\t\tRun as a daemon"
    print "\t--cli to msg\t\t\tSend msg to user once, and quit"
    print "\t--listusers\t\t\tList users"
    print "\t--adduser username password\tAdd user"
    print "\t--remuser\t\t\tRemove users"
    exit()


if __name__ == '__main__':
    runAs = ""
    args = []
    if len(sys.argv) >= 2:
        runAs = sys.argv[1]
        args = sys.argv[1:]
    if runAs == "--daemon":
        run_daemon(args)
    elif runAs == "--cli":
        run_cli(args)
    elif runAs == "--listusers":
        run_listusers(args)
    elif runAs == "--adduser":
        run_adduser(args)
    elif runAs == "--remuser":
        run_remuser(args)
    elif runAs == "--test":
        run_test(args)
    else:
        syntax()
    #main()
    
    
    
    
    
    
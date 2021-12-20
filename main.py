#!/usr/bin/env python3
#########################################################
# Quick and dirty fetch tool for DCG blacklist
#
# by Michele <o-zone@zerozone.it> Pinassi
#
#########################################################
import argparse
import requests
import sqlite3

DB_PATH = "gp.db"
DB=None

# Initialize DB
def db_init():
    try:
        db = sqlite3.connect(DB_PATH)
        cur = db.cursor()
        result = cur.execute('''CREATE TABLE IF NOT EXISTS greenpass
        (id CHAR(256) PRIMARY KEY,
        add_date DATETIME);''')
        db.commit()
    except Exception as e:
        print('DB init() error: %s: %s' % (e.__class__, e))
        return False
    return db

def db_check_and_add(gp):
    if(len(gp) > 0):
        cur = DB.cursor()
        result = cur.execute("SELECT id FROM greenpass WHERE id = '%s';"%(gp))
        if result:
            row = cur.fetchone()
            if row is None:
                # Add GP to database
                try:
                    result = cur.execute("INSERT INTO greenpass(id,add_date) VALUES('%s',date('now'));"%(gp))
                    DB.commit()
                    print("+ %s"%gp)
                    return True
                except Exception as e:
                    print('DB init() error: %s: %s' % (e.__class__, e))
                    return False
    return False

def dcg_fetcher():
    # Initialize counter
    c=0
    # Fetch blacklist
    resp = requests.get('https://get.dgc.gov.it/v1/dgc/settings')
    ret = int(resp.status_code)
    if ret >= 200 and ret < 300:
        data = resp.json()
        for item in data[36]["value"].split(';'):
            if(db_check_and_add(item.strip())):
                c=c+1
        if(c > 0):
            print("Added %d new greenpass to blacklist"%(c))
        else:
            print("No new greenpass added")
    else:
        print("HTTP Error while fetching blacklist: %d"%ret)

def dcg_print():
    cur = DB.cursor()
    for row in cur.execute('SELECT id,add_date FROM greenpass ORDER BY add_date'):
        print("%s"%row[0])

# MAIN()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DCG Italian Blacklist')
    parser.add_argument('-f','--fetch', help='Fetch DCG Italian Blacklist and update DB',action='store_true')
    parser.add_argument('-p','--print', help='Print DCG list', action='store_true')
    args = parser.parse_args()

    # Open DB or create if
    DB = db_init()

    if(args.fetch):
        dcg_fetcher()
    elif(args.print):
        dcg_print()
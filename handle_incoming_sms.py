#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
# encoding=utf8

import requests
import sqlite3 as sql
import threading
import datetime
from keys import LOLTEL_AUTHENTICATION_TOKEN


def add_number_to_database(number):
    con = sql.connect("./database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO phone_numbers (phone_number) VALUES (?)", (number,))
    con.commit()


def delete_number_from_database(number):
    con = sql.connect("./database.db")
    cur = con.cursor()
    cur.execute("DELETE FROM phone_numbers WHERE phone_number=?", (number,))
    con.commit()


def add_sms(sms):
    con = sql.connect("./database.db")
    c = con.cursor()
    c.execute("INSERT INTO smses (sms) VALUES (?)", (sms,))
    con.commit()
    con.close()


def get_previous_smses():
    conn = sql.connect("./database.db")
    c = conn.cursor()
    c.execute('SELECT * FROM smses')
    all_rows = c.fetchall()
    c.close()
    return [row[0] for row in all_rows]


def get_registered_numbers():
    conn = sql.connect('./database.db')
    c = conn.cursor()
    c.execute('SELECT phone_number FROM phone_numbers')
    all_rows = [row[0] for row in c.fetchall()]
    return all_rows


def send_sms(message, recipient):
    recipient = str(recipient)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % LOLTEL_AUTHENTICATION_TOKEN}
    data = {"to_msisdn": str(recipient), "message": message}

    r = requests.post('https://loltelapi.com/api/sms', headers=headers, json=data)
    print(r.url)
    print(r)
    return r


def view_inbox(starts_with="LICHESS", limit=10):
    """
    http://docs.loltelapi.com.s3-website-eu-west-1.amazonaws.com/reference/#sms
    """

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % LOLTEL_AUTHENTICATION_TOKEN}
    data = {"starts_with": starts_with, "limit": limit}

    r = requests.post("https://loltelapi.com/api/sms/search", headers=headers, json=data)

    return r.json()["data"]


def handle_new_sms(number, text):
    nums = get_registered_numbers()
    message = text[7:].lower().strip()

    if message.startswith("start"):
        if number in nums:
            send_sms("You have already subscribed.", number)
        else:
            add_number_to_database(number)
            send_sms("You just subscribed.", number)

    if message.startswith("stop"):
        if number in nums:
            delete_number_from_database(number)
            send_sms("You have been removed.", number)
        else:
            send_sms("You are not registered.", number)


def main():
    for message in view_inbox():
        timestamp = str(message["meta"]["timestamp"])
        if timestamp in get_previous_smses():
            print("Reached a message seen before at %s" % datetime.datetime.fromtimestamp(int(timestamp)).strftime(
                '%d.%m.%Y %H:%M:%S'))
        else:
            add_sms(timestamp)
            print("FROM_NUMBER %s CONTENT %s" % (message["from_number"], message["content"]))
            handle_new_sms(message["from_number"], message["content"])

    threading.Timer(20, main).start()


main()

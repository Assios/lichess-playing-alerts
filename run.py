#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
# encoding=utf8

from keys import LOLTEL_AUTHENTICATION_TOKEN
import requests
import sqlite3 as sql
import threading


def send_sms(message, recipient):
    recipient = str(recipient)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % LOLTEL_AUTHENTICATION_TOKEN}
    data = {"to_msisdn": str(recipient), "message": message}

    r = requests.post('https://loltelapi.com/api/sms', headers=headers, json=data)
    print(r)
    return r


def user_actions(u, state="playing"):
    user = requests.get('https://en.lichess.org/api/user/%s' % u).json()

    return user.get(state)


def fetch_phone_numbers():
    conn = sql.connect("./database.db")
    c = conn.cursor()
    c.execute('SELECT phone_number FROM phone_numbers')
    all_rows = c.fetchall()
    c.close()
    rows = [row[0] for row in all_rows if row[0]]

    return rows


def main(user="assios"):
    next_iteration = 20
    numbers = fetch_phone_numbers()

    game = user_actions(user)

    if game:
        for number in numbers:
            send_sms(user + " is playing a game at " + game, number)
            next_iteration = 60 * 60 * 2
    else:
        print "No games."

    threading.Timer(next_iteration, main).start()


main()

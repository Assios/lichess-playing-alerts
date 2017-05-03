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


def add_sms(time):
    con = sql.connect("./database.db")
    c = con.cursor()
    c.execute("INSERT INTO smses (time) VALUES (?)", (time,))
    con.commit()
    con.close()


def get_previous_smses():
    conn = sql.connect("./database.db")
    c = conn.cursor()
    c.execute('SELECT time FROM smses')
    all_rows = c.fetchall()
    c.close()
    return [row[0] for row in all_rows]


def add_player(player_name):
    con = sql.connect("./database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO players (player_name) VALUES (?)", (player_name,))
    con.commit()


def get_previous_players():
    conn = sql.connect("./database.db")
    c = conn.cursor()
    c.execute('SELECT player_name FROM players')
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

def add_number_player_relation(phone_number, player):
    if not phone_number in get_registered_numbers():
        add_number_to_database(phone_number)
    if not player in get_previous_players():
        add_player(player)

    conn = sql.connect('./database.db')
    c = conn.cursor()
    c.execute('INSERT INTO numbers_players_relation (phone_number, player) VALUES (?, ?)', (phone_number, player))


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

    if message.startswith("yo"):
        add_number_player_relation("4747504585", "galbijjim")
        send_sms("Done", number)


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

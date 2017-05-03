import sqlite3 as sql

conn = sql.connect('database.db')

conn.execute('CREATE TABLE IF NOT EXISTS phone_numbers (phone_id INTEGER PRIMARY KEY AUTOINCREMENT, phone_number TEXT)')

conn.execute('CREATE TABLE IF NOT EXISTS players (player_id INTEGER PRIMARY KEY AUTOINCREMENT, player_name TEXT)')

conn.execute('CREATE TABLE IF NOT EXISTS smses (sms_id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT)')

conn.execute('CREATE TABLE IF NOT EXISTS phone_numbers_players (phone_id INTEGER, player_id INTEGER, PRIMARY KEY (phone_id, player_id))')

conn.close()

def get_int(l):
    if isinstance(l, int):
        return l
    else:
        get_int(l[0])

def add_number_player_relation(number, player):
    conn = sql.connect('./database.db')
    cur = conn.cursor()

    cur.execute('SELECT (phone_id) FROM phone_numbers WHERE phone_number=(?)', (number,))
    phone_id = cur.fetchall()

    if not phone_id:
        cur.execute("INSERT INTO phone_numbers (phone_number) VALUES (?)", (number,))
        phone_id = cur.lastrowid
    else:
        phone_id = get_int(phone_id)

    cur.execute("SELECT (player_id) FROM players WHERE player_name=(?)", (player,))
    player_id = cur.fetchall()

    if not player_id:
        cur.execute("INSERT INTO players (player_name) VALUES (?)", (player,))
        player_id = cur.lastrowid
    else:
        player_id = get_int(player_id)


    if phone_id or player_id:
        cur.execute('INSERT INTO phone_numbers_players (phone_id, player_id) VALUES (?, ?)', (phone_id, player_id))

    conn.commit()

    print "Added %s - %s" (number, player)

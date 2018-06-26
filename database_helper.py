import sqlite3
from flask import g
import math
import random


def connect_db():
    return sqlite3.connect('database.db')


def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_db()
    return db


def init():
    c = get_db()
    query = open('schema.sql', 'r').read()
    cursor = c.cursor()
    cursor.executescript(query)
    c.commit()
    cursor.close()


def create_dummy_entries():
    c = get_db()
    c.execute("INSERT INTO users (email, password, firstname, familyname, gender, city, country)"
              "VALUES ('a@b.c', '12345', 'harry', 'potter', 'Male', 'Hogwarts', 'Magic Land')")
    c.execute("INSERT INTO users (email, password, firstname, familyname, gender, city, country)"
              "VALUES ('Carl@Luck.nl', 'pass1', 'Carl', 'Luck', 'Male', 'Amsterdam', 'Netherlands')")
    c.commit()


def find_user(email, password):
    c = get_db()
    res = c.execute("SELECT * FROM users WHERE email='" + email + "' AND password='" + password + "' LIMIT 1")
    return res.fetchone()


def user_exists(email):
    c = get_db()
    res = c.execute("SELECT * FROM users WHERE email='" + email + "' LIMIT 1")
    return res.fetchone()


def sign_in(email, token):
    c = get_db()
    c.execute("INSERT INTO tokens (email, token) VALUES (?, ?)", (email, token))
    c.commit()


def sign_out(token):
    c = get_db()
    c.execute("DELETE FROM tokens WHERE token = ?", (token,))
    c.commit()


def create_new_user(email, password, firstname, familyname, gender, city, country):
    c = get_db()
    c.execute("INSERT INTO users (email, password, firstname, familyname, gender, city, country)"
              "VALUES (?, ?, ?, ?, ?, ?, ?)", (email, password, firstname, familyname, gender, city, country))
    c.commit()


def get_pwd(email):
    c = get_db()
    pwd = c.execute("SELECT password FROM users WHERE email = ?", email)
    return pwd.fetchone()


def change_password(new_pwd, email):
    c = get_db()
    c.execute("UPDATE users SET password = ? WHERE email = ?", (new_pwd, email))
    c.commit()


def get_profile_picture(email):
    c = get_db()
    picture = c.execute("SELECT picture FROM users WHERE email = ?", email)
    return picture.fetchone()


def change_picture(email, img_type, picture):
    c = get_db()
    img_type = img_type.split("/")[1]
    file_path = "./media/users/" + email + "." + img_type
    picture.save(file_path)
    file_path = "/get_media/users/" + email + "." + img_type
    c.execute("UPDATE users SET picture = ? WHERE email = ?", (file_path, email))
    c.commit()
    return file_path


def get_user_data(email, increase):
    c = get_db()
    user_data = c.execute(
        "SELECT email, firstname, familyname, gender, city, country, picture FROM users WHERE email = ?", (email,))
    if increase:
        profile_views = c.execute("SELECT profile_views FROM users WHERE email = ?", (email,)).fetchone()[0]
        c.execute("UPDATE users SET profile_views = ? WHERE email = ?", (profile_views+1, email))
        c.commit()
    return user_data.fetchone()


def get_user_token(email):
    c = get_db()
    user_token = c.execute("SELECT token FROM tokens WHERE email = ?", (email,))
    return user_token.fetchall()


def add_message(email_from, email_to, message):
    c = get_db()
    msg_type = "text"
    c.execute("INSERT INTO messages (email_from, email_to, msg_type, message) VALUES (?,?,?,?)",
              (email_from, email_to, msg_type, message))
    c.commit()


def add_video_message(email_from, email_to, video_type, video):
    c = get_db()
    msg_type = "video"
    video_type = video_type.split("/")[1]
    letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    video_token = ""
    for i in range(8):
        video_token += letters[int(math.floor(random.random() * len(letters)))]
    file_path = "./media/videos/" + video_token + "." + video_type
    video.save(file_path)
    file_path = "/get_media/videos/" + video_token + "." + video_type
    c.execute("INSERT INTO messages (email_from, email_to, msg_type, message) VALUES (?,?,?,?)",
              (email_from, email_to, msg_type, file_path))
    c.commit()


def get_messages(email_to):
    c = get_db()
    messages = c.execute("SELECT email_from, msg_type, message FROM messages WHERE email_to = ?", (email_to,))
    messages = messages.fetchall()
    messages.reverse()
    return messages


def email_from_token(token):
    c = get_db()
    email_from = c.execute("SELECT email FROM tokens WHERE token = ?", (token,))
    return email_from.fetchone()


def get_chart_field(email, field):
    # fields: users_online, profile_views, messages
    c = get_db()
    if field == "users_online":
        return c.execute("SELECT COUNT(*) FROM tokens").fetchone()[0]
    elif field == "profile_views":
        return c.execute("SELECT profile_views FROM users WHERE email = ?", (email,)).fetchone()[0]
    elif field == "messages":
        return c.execute("SELECT COUNT(*) FROM messages WHERE email_to = ?", (email,)).fetchone()[0]


def get_chart_data(email):
    c = get_db()
    messages = c.execute("SELECT COUNT(*) FROM messages WHERE email_to = ?", email).fetchone()
    users_online = c.execute("SELECT COUNT(*) FROM tokens").fetchone()
    profile_views = c.execute("SELECT profile_views FROM users WHERE email = ?", email).fetchone()
    return [messages[0], users_online[0], profile_views[0]]


def close():
    get_db().close()

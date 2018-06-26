import database_helper as dh
import json
import math
import random


def init_db():
    dh.init()
    dh.create_dummy_entries()
    return json.dumps({"message": "Database initialized."})


def sign_in(email, password):
    res = dh.find_user(email, password)
    if not res:
        # Not logged in
        return json.dumps({"message": "Invalid email or password"}), 501
    else:
        # Logged in
        letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        token = ""
        for i in range(36):
            token += letters[int(math.floor(random.random() * len(letters)))]
        dh.sign_in(email, token)
        return json.dumps({"message": "You are now signed in", "data": token}), 200


def sign_up(email=None, password=None, firstname=None, familyname=None, gender=None, city=None, country=None):
    if dh.user_exists(email):
        return json.dumps({"message": "User with given email already exists"}), 501
    if not email or not password or not firstname or not familyname or not gender or not city or not country:
        return json.dumps({"message": "Incomplete sign up form"}), 501
    if len(password) < 5:
        return json.dumps({"message": "Password too short"}), 501
    dh.create_new_user(email, password, firstname, familyname, gender, city, country)
    return json.dumps({"message": "You are now signed up"}), 200


def sign_out(token):
    dh.sign_out(token)
    return json.dumps({"message": "You have been signed out"}), 200


def sign_out_active(email):
    ws_token = dh.get_user_token(email)
    if len(ws_token) > 1:
        dh.sign_out(ws_token[0][0])
        return ws_token[0]
    return None


def change_password(token, old_pwd, new_pwd):
    email = dh.email_from_token(token)
    old_password = dh.get_pwd(email)
    if old_password[0] != old_pwd:
        return json.dumps({"message": "Old Password incorrect"}), 501
    dh.change_password(new_pwd, email[0])
    return json.dumps({"message": "Password changed"}), 200


def get_user_data_by_token(token):
    email = dh.email_from_token(token)
    if dh.user_exists(email[0]) is None:
        return json.dumps({"message": "No such user"}), 501
    user_data = dh.get_user_data(email[0], False)
    return json.dumps({"message": "User data", "data": user_data}), 200


def get_user_data_by_email(email, token):
    token_email = dh.email_from_token(token)
    if token_email[0] is None:
        return json.dumps({"message": "User not logged in"}), 501
    if dh.user_exists(email) is None:
        return json.dumps({"message": "No such user"}), 501
    user_data = dh.get_user_data(email, True)
    return json.dumps({"message": "User data", "data": user_data}), 200


def get_user_messages_by_token(token):
    email = dh.email_from_token(token)
    messages = dh.get_messages(email[0])
    return json.dumps({"message": "Messages to the user", "data": messages}), 200


def get_user_messages_by_email(email, token):
    token_email = dh.email_from_token(token)
    if token_email[0] is None:
        return json.dumps({"message": "User not logged in"}), 501
    messages = dh.get_messages(email)
    return json.dumps({"message": "Messages to the user", "data": messages}), 200


def post_message(token, email_to, message):
    email_from = dh.email_from_token(token)
    dh.add_message(email_from[0], email_to, message)
    return json.dumps({"message": "Message posted successfully"}), 200


def post_video_message(token, email_to, video_type, video):
    email_from = dh.email_from_token(token)
    dh.add_video_message(email_from[0], email_to, video_type, video)
    return json.dumps({"message": "Message posted successfully"}), 200


def get_profile_picture(token):
    email_from = dh.email_from_token(token)
    picture_src = dh.get_profile_picture(email_from)
    if picture_src:
        return json.dumps({"message": "Profile picture changed", "data": picture_src[0]}), 200
    return json.dumps({"message": "No profile picture found"}), 501


def change_picture(token, img_type, picture):
    email_from = dh.email_from_token(token)
    picture_src = dh.change_picture(email_from[0], img_type, picture)
    return json.dumps({"message": "Profile picture changed", "data": picture_src}), 200


def get_chart_field(email, field):
    field_data = dh.get_chart_field(email, field)
    return json.dumps({"message": "Chart Data", "field": field, "data": field_data})


def get_chart_data(token):
    email_to = dh.email_from_token(token)
    chart_data = dh.get_chart_data(email_to)
    return json.dumps({"message": "Chart Data", "data": chart_data}), 200


# Only for testing
def get_tokens():
    c = dh.get_db()
    res = c.execute("select * from tokens")
    res = res.fetchall()
    return json.dumps({"message": "Token List", "data": res})


# Only for testing
def get_all_messages():
    c = dh.get_db()
    res = c.execute("select * from messages")
    res = res.fetchall()
    return json.dumps({"message": "Message List", "data": res})


# Only for testing
def get_all_users():
    c = dh.get_db()
    res = c.execute("select * from users")
    res = res.fetchall()
    return json.dumps({"message": "User List", "data": res})


# Only for testing
def delete_all_tokens():
    c = dh.get_db()
    c.execute("delete from tokens")
    c.commit()
    return json.dumps({"message": "Tokens deleted"})

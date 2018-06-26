from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from flask import Flask, request, send_from_directory
import server_helper as sh
import database_helper as dh
import json


app = Flask(__name__)
web_socket = {}


@app.route('/')
def root():
    return app.send_static_file('client.html')


@app.route('/api')
def api():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            email = ws.receive()
            # Save new socket
            if email and not web_socket.get(email):
                web_socket[email] = ws
            # Reconnect to closed socket
            if email and web_socket.get(email):
                try:
                    web_socket.get(email).send("")
                except:
                    sh.sign_out_active(email)
                    web_socket[email] = ws
            # Sign out logged in user
            if sh.sign_out_active(email):
                try:
                    web_socket.get(email).send("SIGN OUT")
                except:
                    pass
                web_socket[email] = ws
    return


@app.route("/init_db", methods=["GET"])
def init_db():
    return sh.init_db()


@app.route('/sign_in', methods=["POST"])
def sign_in():
    message = sh.sign_in(request.get_json()['email'], request.get_json()['password'])
    update_charts("all", "users_online")
    return message


@app.route("/sign_up", methods=["POST"])
def sign_up():
    json = request.get_json()
    return sh.sign_up(json['email'], json['password'], json['firstname'], json['familyname'],
                      json['gender'], json['city'], json['country'])


@app.route("/sign_out", methods=["POST"])
def sign_out():
    email = dh.email_from_token(request.get_json()['token'])
    if web_socket.get(email[0]):
        del web_socket[email[0]]
    message = sh.sign_out(request.get_json()['token'])
    update_charts("all", "users_online")
    return message


@app.route("/change_password", methods=["POST"])
def change_password():
    return sh.change_password(request.get_json()['token'], request.get_json()['oldPassword'],
                              request.get_json()['newPassword'])


@app.route("/get_user_data_by_token/<token>", methods=["GET"])
def get_user_data_by_token(token):
    return sh.get_user_data_by_token(token)


@app.route("/get_user_data_by_email/<email>/<token>", methods=["GET"])
def get_user_data_by_email(email, token):
    message = sh.get_user_data_by_email(email, token)
    if message[1] == 200 and web_socket.get(email):
        update_charts(email, "profile_views")
    return message


@app.route("/get_user_messages_by_token/<token>", methods=["GET"])
def get_user_messages_by_token(token):
    return sh.get_user_messages_by_token(token)


@app.route("/get_user_messages_by_email/<email>/<token>", methods=["GET"])
def get_user_messages_by_email(email, token):
    return sh.get_user_messages_by_email(email, token)


@app.route("/post_message", methods=["POST"])
def post_message():
    message = sh.post_message(request.get_json()['token'], request.get_json()['email'], request.get_json()['message'])
    update_charts(request.get_json()['email'], "messages")
    return message


@app.route("/post_video_message", methods=["POST"])
def post_video_message():
    message = sh.post_video_message(request.form['token'], request.form['email'], request.form['type'],
                                    request.files['video'])
    update_charts(request.get_json()['email'], "messages")
    return message


@app.route("/get_profile_picture/<token>", methods=["GET"])
def get_profile_picture(token):
    return sh.get_profile_picture(token)


@app.route("/change_picture", methods=["POST"])
def change_picture():
    return sh.change_picture(request.form['token'], request.form['type'], request.files['picture'])


@app.route("/get_chart_data/<token>", methods=["GET"])
def get_chart_data(token):
    return sh.get_chart_data(token)

@app.route("/get_media/<folder>/<filename>", methods=["GET"])
def get_media(folder, filename):
    return send_from_directory('media/' + folder + '/', filename)

# Send "CHART UPDATE" to all active clients
def update_charts(email, field):
    data_set = sh.get_chart_field(email, field)
    if email == "all":
        # Send to all users connected on socket
        for mail_address in web_socket:
            try:
                web_socket.get(mail_address).send(data_set)
            except:
                continue
    else:
        # Send to the given email
        if web_socket.get(email):
            web_socket.get(email).send(data_set)


def run_server():
    app.debug = True
    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()


if __name__ == '__main__':
    run_server()

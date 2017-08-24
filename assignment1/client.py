#!/usr/bin/env python3
import getpass
import pickle
import sys
import zmq

import encrypt

CONNECT = 'tcp://localhost:8001'


if __name__ == '__main__':
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect(CONNECT)

    user = input("Enter username:")

    mesg = [b'start_session', pickle.dumps({'user': user})]
    socket.send_multipart(mesg)

    mesg = socket.recv_multipart()
    if mesg[0] == b'no_such_user':
        print("No such user")
        sys.exit(1)
    elif mesg[0] == b'auth_challenge':
        challenge = pickle.loads(mesg[1])
        password = getpass.getpass("Enter password:").encode()
        password = encrypt.reduce_key(password)
        response = encrypt.encrypt_bytes(challenge, password)
        mesg = [b'auth_response', pickle.dumps({'user': user,
                                                'response': response})]

        socket.send_multipart(mesg)
        mesg = socket.recv_multipart()
        if mesg[0] == b'auth_pass':
            print("Logged in")
            sys.exit(0)
        else:
            print("Incorrect credentials")
            sys.exit(1)
    while True:
        mesg = socket.recv()
        pass

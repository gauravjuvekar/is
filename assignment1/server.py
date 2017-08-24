#!/usr/bin/env python3
import logging
import pickle
import zmq

import encrypt
import secrets


logging.basicConfig()
log = logging.getLogger(__name__)

BIND = 'tcp://*:8001'


if __name__ == '__main__':
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)
    socket.bind(BIND)
    open_connections = {}
    while True:
        mesg = socket.recv_multipart()
        if mesg[0] == b'start_session':
            body = pickle.loads(mesg[1])
            if body['user'] not in secrets.secrets:
                socket.send_multipart([b'no_such_user'])
                log.info('User %s is not known', body['user'])
                continue

            auth_challenge = encrypt.get_seed()
            socket.send_multipart([b'auth_challenge',
                                   pickle.dumps(auth_challenge)])
            open_connections[body['user']] = {'auth_challenge': auth_challenge}
            log.info('Challenge sent for user %s', body['user'])
            continue
        elif mesg[0] == b'auth_response':
            body = pickle.loads(mesg[1])
            if body['user'] not in open_connections:
                socket.send_multipart([b'auth_response without request'])
                log.info('Spurious response for user %s', body['user'])
                continue
            user = body['user']
            response = body['response']

            challenge = open_connections[user]['auth_challenge']
            password = secrets.secrets[user].encode()
            password = encrypt.reduce_key(password)

            response = encrypt.decrypt_bytes(response, password)
            if response == open_connections[user]['auth_challenge']:
                socket.send_multipart([b'auth_pass'])
                log.info('User %s authenticated', user)
            else:
                socket.send_multipart([b'auth_fail'])
                log.info('Auth fail for user %s', user)

        elif mesg[0] == b'end_session':
            pass

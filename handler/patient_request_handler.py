import base64
import http
import logging
import secrets
import shelve
import sys
import time
import json
import config
from http import HTTPStatus


def register():
    pass


def handle(path_components, data):
    """
    :param path_components: list
    :param data: dict
    :return:
    """
    if len(path_components) < 1:
        return

    if path_components[0] == "register":
        user_id = data['user_id']
        passwd = data['passwd']

        # save the user_id and password on database
        with shelve.open(config.user_db_path) as udb:
            # TODO: implement check for existing user names (later)
            udb[user_id] = passwd

        return HTTPStatus.OK, None



    return

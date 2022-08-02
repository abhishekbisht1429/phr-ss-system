import json
import secrets
import sys
import time
import shelve
import logging


def register():
    pass


def handle(path_components, msg):
    """
    :param path_components: list
    :param msg: dict
    :return:
    """
    if len(path_components) < 1:
        return

    return
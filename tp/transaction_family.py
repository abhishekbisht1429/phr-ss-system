import hashlib
import sys

import cbor2

NAME = 'thesis'
NAMESPACE = hashlib.sha512(NAME.encode('utf-8')).hexdigest()[:6]
VERSION = '1.0'

EVENT_SEARCH_COMPLETE = NAME+'/'+'search_complete'
# def generate_address(key):
#     return NAMESPACE + hashlib.sha512(str(key).encode('utf-8')).hexdigest()[
#                        -64:]


class TransactionPayload:

    def __init__(self, payload):
        action, data = cbor2.loads(payload)
        self._action = action
        self._data = data
        # if action == constants.ACTION_SET:
        #     self._addr = data[0]
        #     self._value = data[1]
        # elif action == constants.ACTION_SEARCH:
        #     self._data = data

    @property
    def action(self):
        return self._action

    @property
    def data(self):
        return self._data
    # @property
    # def address(self):
    #     return self._addr
    #
    # @property
    # def value(self):
    #     return self._value

    @classmethod
    def from_bytes(cls, payload):
        return cls(payload)


class State:

    def __init__(self, context):
        self._context = context

    def set(self, addr, value):
        """
        :param key: bytes
        :param value: string
        :return:
        """
        # address = generate_address(key)
        self._context.set_state({addr: value})


    def get(self, addr_hex):
        entry_list = self._context.get_state([addr_hex])
        if len(entry_list) > 0:
            return entry_list[0]
        return None

    def delete(self, addr):
        # address = generate_address(key)
        self._context.delete_state([addr])

    def add_event(self, event_type, attributes, data):
        self._context.add_event(
            event_type=event_type,
            attributes=attributes,
            data=data
        )

class InvalidAction(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg

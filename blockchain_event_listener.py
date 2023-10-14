import logging
import os
import time

import zmq
from sawtooth_sdk.protobuf.client_event_pb2 import ClientEventsSubscribeRequest, \
    ClientEventsSubscribeResponse
from sawtooth_sdk.protobuf.events_pb2 import EventSubscription, EventFilter, \
    EventList
from sawtooth_sdk.protobuf.validator_pb2 import Message

import config


# Two ways to do -
# 1. create listener before every search request and destroy it after that
# 2. create listener during startup send the search request and store the
# results of events in a dictionary keyed by timestamp.
class EventListener:
    def __init__(self, url, subscription):
        self._url = url

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.DEALER)
        self._socket.connect(url)

        self._subscribe(subscription)
        self._listening = False

        # TODO: use a circular buffer here
        self._events_buffer = dict()

    def _subscribe(self, subscription):
        logging.debug('subscribe')
        logging.debug('URL: ' + self._url)
        # subscription = EventSubscription(
        #     event_type='thesis/search_complete',
        #     filters=[EventFilter(
        #         key='id',
        #         # TODO: set the match_string to a specific value unique for
        #         #  the hospital
        #         match_string='.*',
        #         filter_type=EventFilter.REGEX_ANY
        #     )]
        # )

        request = ClientEventsSubscribeRequest(
            subscriptions=[subscription]
        ).SerializeToString()

        msg = Message(
            correlation_id=os.urandom(8).hex(),
            message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
            content=request
        )

        self._socket.send_multipart([msg.SerializeToString()])
        resp = self._socket.recv_multipart()[-1]
        msg = Message()
        msg.ParseFromString(resp)

        # Validate the response type
        # print(msg.message_type)
        if msg.message_type != Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE:
            raise Exception("Unexpected Message Type")

        # Parse the response
        response = ClientEventsSubscribeResponse()
        response.ParseFromString(msg.content)

        # Validate the response status
        if response.status != ClientEventsSubscribeResponse.OK:
            logging.error("Subscription failed: {}".format(
                response.response_message))
            raise Exception("Subscription Failed")
        else:
            print("success")
            logging.info("Search Event Listener subscribed successfully")

    def listen(self):
        logging.info("Started Listening for Events")
        self._listening = True
        while self._listening:
            print("inside listening for event loop")
            resp = self._socket.recv_multipart()[-1]
            msg = Message()
            msg.ParseFromString(resp)

            if msg.message_type != Message.CLIENT_EVENTS:
                logging.info("Invalid Message type received")
                continue

            logging.info("Valid message type received")

            event_list = EventList()
            event_list.ParseFromString(msg.content)
            for event in event_list.events:
                logging.debug('event occurred' + str(event.event_type) +
                              str(event.attributes))
                self._events_buffer[event.attributes[0].value] = event.data

        logging.info("Stopped Listening for EVents")

    def stop_listening(self):
        # TODO: implement a method by which the listener will stop for sure
        self._listening = False

    def get_event(self, id, timeout=1000):
        count = 0
        while id not in self._events_buffer:
            count += 1
            time.sleep(count * 100 / 1000)
            if count * 100 == timeout:
                raise Exception("Timed out") # TODO: use an appropriate
                # exception for timeout

        event_data = self._events_buffer[id]
        # TODO: use circular buffer
        del self._events_buffer[id]
        return event_data

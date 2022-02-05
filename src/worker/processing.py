import json
import logging
import datetime
import threading


def execute_processing_query(ch, method, properties, body):
    request_id = json.loads(body.decode()).request_id

    logging.info(f"[{datetime.datetime.now()}:{threading.current_thread().ident}] Processing request #{request_id}")

    ###
    # TODO: Processing action
    ###

    # Assure message delivery
    logging.info(f"[{datetime.datetime.now()}:{threading.current_thread().ident}] Finish processing request #{request_id}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

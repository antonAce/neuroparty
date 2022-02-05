import pika
import logging
import datetime
import threading

from processing import execute_processing_query
from settings import CONNECTION_HOST, MSG_QUEUE_NAME


logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)

connection_params = pika.ConnectionParameters(host=CONNECTION_HOST)
connection = pika.BlockingConnection(connection_params)

channel = connection.channel()
channel.queue_declare(queue=MSG_QUEUE_NAME, durable=True)


if __name__ == "__main__":
    try:
        ###
        ### Key entry point of the processing worker.
        ###
        logging.info(f"[{datetime.datetime.now()}:{threading.current_thread().ident}] Worker started listening on amqp://{CONNECTION_HOST}:{MSG_QUEUE_NAME}.")

        # Ensure that only single request is processed simultaneously.
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=MSG_QUEUE_NAME, on_message_callback=execute_processing_query)
        channel.start_consuming()
    except KeyboardInterrupt as ex:
        logging.info(f"[{datetime.datetime.now()}:{threading.current_thread().ident}] Worker gracefully stopped.")
    finally:
        connection.close()

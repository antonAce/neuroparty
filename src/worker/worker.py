import pika
import logging
import datetime
import threading

from processing import execute_processing_query
from settings import QUEUE_CONNECTION_HOST, QUEUE_MSG_QUEUE_NAME, QUEUE_BLOCKED_CONNECTION_TIMEOUT

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)

# Disable verbose logging for message queue
pika_logger = logging.getLogger('pika')
pika_logger.setLevel(logging.WARNING)

connection_params = pika.ConnectionParameters(host=QUEUE_CONNECTION_HOST,
                                              blocked_connection_timeout=QUEUE_BLOCKED_CONNECTION_TIMEOUT)
connection = pika.BlockingConnection(connection_params)

channel = connection.channel()
channel.queue_declare(queue=QUEUE_MSG_QUEUE_NAME, durable=True)

if __name__ == "__main__":
    try:
        # Key entry point of the processing worker.
        logging.info(f"[{datetime.datetime.now()}:{threading.current_thread().ident}] Worker started listening " +
                     f"on amqp://{QUEUE_CONNECTION_HOST}:{QUEUE_MSG_QUEUE_NAME}.")

        # Ensure that only single request is processed simultaneously.
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUE_MSG_QUEUE_NAME, on_message_callback=execute_processing_query)
        channel.start_consuming()
    except KeyboardInterrupt as ex:
        logging.info(f"[{datetime.datetime.now()}:{threading.current_thread().ident}] Worker gracefully stopped.")
    finally:
        connection.close()

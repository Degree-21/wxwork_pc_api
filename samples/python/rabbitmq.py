import json

import pika


# 用于把消息放入其中 进行消费


class MqBase:
    """
    通过重新生成这个类可以实现多个的方法 先实现消息入队列 其他的服务端则可以通过 rabbitmq 操作
    """
    exchange_name = "wx_work_exchange"
    queue_name = "wx_word_message"
    routing_key = "wx_word_message"
    exchange_type = "direct"


def conn_mq():
    auth = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.187', port=5672, credentials=auth))
    channels = connection.channel()
    channels.exchange_declare(exchange=product.exchange_name, exchange_type=product.exchange_type, durable=True)
    channels.queue_declare(queue=product.queue_name)
    channels.queue_bind(queue=product.queue_name, exchange=product.exchange_name, routing_key=product.routing_key)
    return channels


product = MqBase()
channel = conn_mq()


class WeWorkMessage:
    client_id = ""
    message_type = ""
    message_data = ""


def push_we_work_message(info):
    if isinstance(info, WeWorkMessage):
        if channel is None:
            conn_mq()
        result = json.dumps(info.__dict__)
        res = channel.basic_publish(exchange=product.exchange_name, routing_key=product.routing_key, body=result)
        print("发送进消息队列结果:{}".format(res))
        # connection.close()
    else:
        raise Exception("传递消息体有误，请重新传递")


def callback(ch, method, properties, body):
    print("================================")
    print(" [x] Received %r" % body)


def consume_message():
    if channel is None:
        conn_mq()
    channel.basic_consume(on_message_callback=callback,
                          queue=product.queue_name,
                          auto_ack=True)
    channel.start_consuming()

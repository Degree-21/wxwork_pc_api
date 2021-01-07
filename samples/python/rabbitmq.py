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


class WeWorkMessage:
    client_id = ""
    message_type = ""
    message_data = ""


class PushWeWorkMessage:
    client_id = ""
    conversation_id = ""
    content = ""
    message_type = ""
    row = ""


class RabbitMq:
    conn = {}
    channel = {}
    model = {}

    def __init__(self, dataModel):
        self.conn_mq(dataModel)

    def conn_mq(self, dataModel):
        if isinstance(dataModel, MqBase):
            print("111111进入")
            print(self.conn)
            print(":==================")
            self.model = dataModel
            auth = pika.PlainCredentials('guest', 'guest')
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='192.168.0.187', port=5672, credentials=auth))
            channel = connection.channel()

            channel.exchange_declare(exchange=dataModel.exchange_name, exchange_type=dataModel.exchange_type,
                                     durable=True)
            channel.queue_declare(queue=dataModel.queue_name)
            channel.queue_bind(queue=dataModel.queue_name, exchange=dataModel.exchange_name,
                               routing_key=dataModel.routing_key)
            self.conn = connection
            self.channel = channel

    def push_we_work_message(self, info):
        if isinstance(info, WeWorkMessage):
            if self.conn.is_closed:
                self.conn_mq(self.model)
            result = json.dumps(info.__dict__)
            res = self.channel.basic_publish(exchange=self.model.exchange_name, routing_key=self.model.routing_key, body=result)
            print("发送进消息队列结果:{}".format(res))
            # channel.close()
            return
        else:
            raise Exception("传递消息体有误，请重新传递")

    # def callback(ch, method, properties, body):
    #     print("================================")
    #     print(" [x] Received %r" % body)

    def consume_message(self, callback):
        self.channel.basic_consume(
            on_message_callback=callback,
            queue=self.model.queue_name,
            auto_ack=True
        )
        # channel.basic_consume(on_message_callback=callback,
        #                       queue=product.queue_name,
        #                       auto_ack=True)
        self.channel.start_consuming()
        pass
    # if connection.is_closed:
    #     conn_mq()
    # channel.basic_consume(on_message_callback=callback,
    #                       queue=product.queue_name,
    #                       auto_ack=True)
    # channel.start_consuming()

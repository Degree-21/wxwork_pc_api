# -*- coding: utf-8 -*-

import json
import time

import rabbitmq
import wxwork
from wxwork import WxWorkManager, MessageType

wxwork_manager = WxWorkManager(libs_path='../../libs')


# 这里测试函数回调
@wxwork.CONNECT_CALLBACK(in_class=False)
def on_connect(client_id):
    print('[on_connect] client_id: {0}'.format(client_id))


@wxwork.RECV_CALLBACK(in_class=False)
def on_recv(client_id, message_type, message_data):
    print('[on_recv] client_id: {0}, message_type: {1}, message:{2}'.format(client_id,
                                                                            message_type, json.dumps(message_data)))


@wxwork.CLOSE_CALLBACK(in_class=False)
def on_close(client_id):
    print('[on_close] client_id: {0}'.format(client_id))


class EchoBot(wxwork.CallbackHandler):

    @wxwork.RECV_CALLBACK(in_class=True)
    def on_message(self, client_id, message_type, message_data):
        # 通过消息队列来实现其他客户端的无缝衔接
        message_class = rabbitmq.WeWorkMessage()
        message_class.client_id = client_id
        message_class.message_type = message_type
        message_class.message_data = message_data
        mq = rabbitmq.RabbitMq(rabbitmq.MqBase())
        mq.push_we_work_message(message_class)
        print("推入消息队列完成")

        # print("===结束==")
        # # 如果是文本消息，就回复一条消息
        # if message_type == MessageType.MT_RECV_TEXT_MSG:
        #     reply_content = u'😂😂😂你发过来的消息是：{0}'.format(message_data['content'])
        #     time.sleep(2)
        #     wxwork_manager.send_text(client_id, message_data['conversation_id'], reply_content)

    def on_mq_push_message(self):
        exchange = rabbitmq.MqBase()
        exchange.exchange_name = "wx_work_push_exchange"
        exchange.queue_name = "wx_word_push_message"
        exchange.routing_key = "wx_word_push_message"
        exchange.exchange_type = "direct"
        mq = rabbitmq.RabbitMq(exchange)
        mq.consume_message(self.call_back_)

    def call_back_(self, ch, method, properties, body):
        try:
            info = json.loads(str(body, 'utf-8'))
            print(info)
            data_model = rabbitmq.PushWeWorkMessage()
            data_model.client_id = info["client_id"]
            data_model.conversation_id = info["conversation_id"]
            data_model.content = info["content"]
            data_model.message_type = info["message_type"]
            data_model.row = info["row"]
            if data_model.message_type == MessageType.MT_RECV_TEXT_MSG:
                reply_content = u'😂😂😂你发过来的消息是：{0}'.format(data_model.content)
                # time.sleep(2)
                print(reply_content)
                res = wxwork_manager.send_text(data_model.client_id, data_model.conversation_id, data_model.content)
                print(res)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    echoBot = EchoBot()

    # 添加回调实例对象
    wxwork_manager.add_callback_handler(echoBot)
    wxwork_manager.manager_wxwork(smart=True)
    echoBot.on_mq_push_message()

    # todo 改为多进程收发
    # 阻塞主线程
    while True:
        time.sleep(0.5)

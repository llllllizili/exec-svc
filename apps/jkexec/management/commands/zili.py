from django.core.management.base import BaseCommand, CommandError

from utils.rabbitmqApi.mq import MessageQueueHandle

class Command(BaseCommand):
    help = 'zili command test'

    # 接收参数.可删
    def add_arguments(self, parser):
        parser.add_argument('args1', type=str, help='args 1')
        parser.add_argument('args2', type=str, help='args 2')

    def handle(self, *args, **options):
        # 参数
        args1 = options['args1']
        args2 = options['args2']
        mqhandle = MessageQueueHandle('1111')
        aaa = mqhandle.zili()
        print(aaa)
        self.stdout.write(self.style.SUCCESS('{} Successfully {}'.format('接收args1成功', args1)))  #可以自定制在控制台输出的内容
        self.stdout.write(self.style.SUCCESS('{} Successfully {}'.format('接收args2成功', args2)))  #可以自定制在控制台输出的内容

# python manager.py zili  args1 args 1



# import json
# from django.core.management.base import BaseCommand, CommandError

# from utils.rabbitmqApi.mq import MessageQueueHandle


# class ListenError(Exception):
#     pass

# class Command(BaseCommand):
#     help = 'RPA监听'

#     def handle(self, *args, **options):
#         def __listen_callback(ch, method, properties, body):
#             print("_____________________________________mq - _listen_rpa_mq_status")
#             print(type(body))
#             print(body)


#             data = json.loads(body.decode())
#             rpa_status = data.get('status')
#             print(rpa_status)

#             if rpa_status == 'success':
#                 print('success')
#                 self.channel.stop_consuming()
#             else:
#                 raise ListenError('执行RPA task失败')
#         mqhandle = MessageQueueHandle('1111')
#         aaa = mqhandle._listen_rpa_mq_status(__listen_callback)
#         print(aaa)



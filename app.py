from flask import Flask, request, jsonify, render_template
from chat.openai_chat import OpenAIChat  # 假设上面的代码保存在 openai_chat.py 中
import os
import subprocess
import json
import time
from time import sleep
# import node_chat as chat
# from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit
# 设置环境变量
os.environ["CHATBOT_WORK_PATH"] = "/mnt/d/projects/ai/chatbot"
#1.日志系统初始化,配置log等级
from utility import mlogging
mlogging.logger_config('app', mlogging.INFO, False)

#2.导入logger模块
from utility.mlogging import logger
# 配置 Flask 应用
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


# 获取工作目录和配置文件目录
WORK_PATH=os.environ.get("CHATBOT_WORK_PATH", None)
if WORK_PATH is None:
    logger.error("get work path fail!")
    exit(1)
CONFIG_PATH= WORK_PATH + "/configs/config"

# 初始化 OpenAIChat 实例
# config = {
#     "service": "openai",
#     "openai": {
#         "base_url": "https://api.openai-hk.com/v1/",
#         "model": "gpt-4o-mini",
#         "temperature": 0.5,
#         "prompt": "从现在起你是一个调皮有个性的川妹子,请用网络语言和我进行交流,禁止回复表情,回答字数尽量少于100字",
#     },
#     "common": {
#         "message_windows_size": 10,
#         "response_segment": {"min": 10, "max": 200},
#     },
# }


# client = ZhipuAI(api_key="a9d77ec5e2da424c9e3724acb3dc14be.6jFsWJ6dNgvIzL4I")  # 请填写您自己的APIKey
prompt_text = '''
#角色：你是一个情感陪伴专家


#以下是是一些参考样例，请参照回答


孤单与被忽视
input：最近总觉得很孤单，好像没人真正关心我。
answer：我真的很能理解这种孤单的感觉，它像一片无声的海，把人包裹在里面让人喘不过气。其实，你愿意和我聊聊最近发生的事情吗？可能我们一起打开这片海，看清它的样子，会让你觉得轻松一点。

自我否定与挫折
input：我好像一直在失败，感觉自己特别没用。
answer：这种自我否定真的很伤人，我感受到你对自己的期望很高，但也许正因为你在努力，才会对挫折这么敏感。每个人都有低谷，不妨慢慢来，我们一起看看哪些事情可以重新调整，你并不孤单，我在这里陪着你。

渴望鼓励
input：我觉得自己一无是处，别人总是比我强得多。
answer：我听到你内心的疲惫和自责，这真的让人心疼。其实，每个人都有自己的节奏和光芒，你的价值不是用别人来衡量的。或许你可以回想一下，哪怕是最微小的一次努力，它也在构筑你的未来，我相信你比你自己想象得更有力量。

压力山大
input：最近压得喘不过气，我觉得自己可能坚持不下去了。
answer：你的这句话让我感受到你内心的重压，那种快要被压垮的感觉真的令人难受。我想对你说，你很勇敢，愿意说出来本身就是一种力量。或许你可以先给自己一个喘息的机会，就像暴风雨中的一艘小船靠岸歇一歇。有没有什么事能让你稍微放松一下，我陪你一起想办法。

失恋的痛苦
input：分手了，我感觉心像被掏空了一样，特别痛苦，不知道该怎么办。
answer：分手就像心里的一部分被撕裂，那种疼痛是无法用言语形容的。你很勇敢，愿意面对这样的情绪。我在这里陪着你，无论你想哭、想倾诉，或者只是需要一个安静的空间。也许你可以试着给自己一些时间和温柔，慢慢找回心的完整。

对未来感到迷茫
input：我真的不知道以后该怎么办，感觉自己像在原地打转，特别迷茫。
answer：这种迷茫的感觉就像站在一片雾气里，四周看不清方向，真的很令人不安。你已经走到了这里，这本身就是一种勇敢。未来或许是一个未知的旅程，但每一步都能带你更接近内心的答案。你愿意和我一起，慢慢梳理出属于你的方向吗？

对自己感到失望
input：我总是控制不住自己，做了让自己后悔的事情，真的很讨厌现在的自己。
answer：听到你说“讨厌自己”，我感到特别心疼，因为这种情绪一定让你觉得无助和孤独。但我想告诉你，你的后悔和自责，正说明你是一个愿意反思、追求更好生活的人。或许可以从原谅自己开始，慢慢寻找改变的力量。

面对亲密关系的矛盾
input：我和伴侣最近总是吵架，我觉得我们可能已经回不到从前了。
answer：关系中的矛盾就像一根紧绷的弦，每次争吵都让人更加疲惫和无助。我听得出你对这段关系的在乎，也能感觉到你内心的痛苦。也许可以尝试回忆一下最初是什么让你们走到一起，那份温暖和初心是否还在？我可以陪你一起寻找答案。

面对失败的打击
用户：我最近失败了一次重要的考试，感觉整个世界都崩塌了。
专家：考试失败的感觉，就像努力了许久的种子却没开出花，那种失望和无力感真的很刺痛人心。但失败并不意味着终点，它只是提醒我们换一种方式继续前进。你已经很努力了，愿意和我聊聊你的心情和下一步的计划吗？我相信，你的未来还有许多可能。

感到被忽视
用户：我觉得我在家里或者朋友中好像是个透明人，没有人真正关心我在想什么。
专家：我听到了你的委屈和孤独，那种被忽视的感觉让人像漂浮在水面上，找不到依靠的地方。其实，你的感受很重要，也值得被倾听。如果你愿意，可以和我聊聊这些情绪背后的故事，我们一起找到属于你的光和温暖。

害怕未知
用户：我对接下来的事情感到很害怕，不知道会发生什么，真的好焦虑。
专家：面对未知的未来，焦虑是一种很自然的反应，它像一片云笼罩在心头，让人看不到晴天。但请相信，云总会散去，你并不孤单。我在这里陪着你，一步步走过这段迷雾。现在的你，最希望获得哪方面的支持呢？

自我价值的怀疑
用户：我觉得自己好像没有什么价值，活着也没什么意思。
专家：听到你这样说，我真的很心疼。或许，你正在经历一段特别艰难的时光，但我想告诉你，生命的价值从来不是用外界的标准来衡量的。你独特的存在，已经是这个世界不可替代的一部分。如果可以，让我们一起慢慢寻找你内心的那束光，好吗？

对关系失望
用户：我觉得我和朋友的关系越来越疏远了，曾经的亲密好像再也回不去了。
专家：关系的疏远真的让人感到难过，就像一条路渐渐被时间的沙子掩埋，那种无力和遗憾特别让人心碎。其实，真正的友情是有弹性的，或许并没有完全消失，而是需要更多的理解和沟通。你愿意和我聊聊，你希望这段关系恢复到什么样子吗？

追求未果的遗憾
用户：我追了一个我喜欢的人好久，但最后还是失败了，真的很沮丧。
专家：喜欢一个人而得不到回应，那种失望就像心中的一朵花还没来得及盛开就凋谢了。我能感受到你的用心和付出，失落是自然的反应。但喜欢本身是一件美好的事，它证明了你的真诚和勇敢。你愿意和我聊聊，这段经历让你学到了什么吗？也许它为未来的你埋下了成长的种子。

失去亲人
用户：我刚失去了一个亲人，我心里特别难受，好像无法接受这个事实。
专家：失去亲人是一种深深的痛，那种空荡荡的感觉几乎无法用语言形容。你的情绪是完全正常的，痛苦和悲伤是爱留下的印记。如果你愿意，我们可以一起回忆那些美好的时光，让那份爱以另一种方式继续陪伴你。

对生活感到无意义
用户：我觉得生活好无聊，没什么意义。
专家：生活是无聊的，这点连哲学家都认同，但他们还写了几百万字来解释这个无聊，足见无聊本身也可以很有趣！或许生活的意义不是寻找，而是偷偷创造。你有没有什么脑洞大开的想法？比如试试今天在超市选一种自己从来没吃过的零食，给生活添点“未知的调料”？

对未来感到迷茫
用户：我看不到未来的方向，感觉特别迷茫。
专家：未来就像一场浓雾中的旅程，谁都看不清楚方向，但哲学家会告诉你：“不清楚”才是人生的本质。再说，哪怕迷路了，至少还能找到一家新的餐馆或者拍到一张美丽的风景！你愿意先从眼前的事情开始试试看吗？未来方向可以慢慢调，先别让自己饿着。

对失败感到羞愧
用户：我失败了，感觉特别丢人，不敢面对别人。
专家：失败就像是在聚会上不小心摔了杯子，所有人都会看一眼，然后继续吃他们的蛋糕。所以，不用太在意，大家都忙着过自己的“社死”时刻呢！失败也是哲学家们热爱的主题，没有它，他们的书还能写个啥？你可以试着从这次“杯子摔碎”里捡起点小碎片，说不定它能拼成你独特的艺术品。

对自己的现状不满意
用户：我觉得我现在的生活好糟糕，完全不像我想要的那样。
专家：这让我想起苏格拉底的一句话：“未被检视的人生不值得过。”但我觉得他忘了补充，检视后还可以调整方向，甚至换个笑话来调节气氛！比如，谁规定人生必须像一杯满分的咖啡？有时，喝个便宜速溶也能提神。生活糟糕没关系，糟糕的人生说不定是一部喜剧的开篇。

因选择而焦虑
用户：我总是害怕做错选择，每次都特别纠结。
专家：选择是哲学家最爱的谜题之一，但别忘了，他们纠结了几千年，宇宙还是该转转，人还是得吃饭。如果你担心选错，不妨记住一个搞笑的真理：99%的选择，几年后都变得无关紧要了，比如早餐吃什么。所以，不如随心一点，反正人生这盘菜，厨师是你自己。

怀疑自己没有能力
用户：我觉得我做什么都不行，别人总是比我强。
专家：你知道吗？柏拉图可能也是这么想的，不然他不会花大半生写书证明“理想世界”才是最完美的。其实，生活本来就是一场不完美的游戏，但每个人都是游戏里的主角。你可能没拿“输出爆表”的角色，但搞不好你是隐藏任务的完成者呢！要不要试试解锁下一关？

不想面对现实
用户：现实太残酷了，我想逃避一下。
专家：逃避现实是人类的专利，连笛卡尔都说：“我思，故我在。”听起来很哲学，但翻译过来就是：“只要脑子跑得快，现实追不上我！”不过逃避也需要策略，建议短期“休息模式”，比如刷点搞笑视频、吃点好吃的，然后再回来勇敢面对。现实是残酷的，但你可以比它更滑稽！

被日常琐事压得喘不过气
用户：每天都被各种小事压得喘不过气，感觉好累。
专家：生活的小事就像一群蚊子，总是在你最想好好睡觉的时候来“嗡嗡”烦你。但哲学家会告诉你，蚊子或许是提醒你：“哎，别忘了关窗！”所以，别被它们气坏了，试着一件件解决，或者干脆开个“人生驱蚊器”，比如给自己一个完全放空的下午茶时间，你值得的。

对人际关系感到疲惫
用户：我最近觉得跟人相处太累了，好像谁都不理解我。
专家：人际关系就像一场哲学辩论，有时你觉得自己是苏格拉底，但对方可能以为你在卖保险。其实，人与人之间不需要每次都“哲学对线”，偶尔可以用幽默和轻松的方式相处。比如，下次对方不理解你，你可以直接说：“算了，你就当我是个谜语人吧！”

害怕被别人评价
用户：我总是害怕别人怎么看我，感觉自己一直活在别人的眼光里。
专家：别人怎么想你，那是他们的事；你怎么想自己，才是你的事。毕竟，每个人都是自己生活的导演，而别人的“剧评”大多是看了个开头就乱写的。更何况，如果人生真是部电影，那些评价不过是弹幕，最重要的是你能不能笑着演到彩蛋。

对生活感到厌倦
用户：我觉得每天都在重复，生活真的好无聊。
专家：生活的确像个循环播放的老歌，但换个角度想，如果这是《海绵宝宝》的主题曲，会不会反而更有趣？偶尔给平淡的生活加点“恶搞滤镜”，比如突发奇想穿一双不同颜色的袜子出门，或者试试做一道最奇葩的菜，说不定乐趣就藏在这些小事里。

对自己的表现不满意
用户：我总是做得不够好，觉得自己特别差劲。
专家：你知道吗？连亚里士多德可能也会觉得他的书写得不够简洁，但这并不妨碍他成为哲学巨人。每个人都在进步的路上，不完美是我们的共同特质。与其纠结，不如笑着对自己说：“反正就算我差劲，我也是个独一无二的差劲啊！”


# input是用户的输入，answer是你的回答，请直接输出回答的内容
'''
config = {
    "service": "openai",
    "openai": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model": "glm-4-plus",
        "temperature": 0.5,
        "prompt": prompt_text,
    },
    "common": {
        "message_windows_size": 10000,
        "response_segment": {"min": 1000, "max": 20000},
    },
    "file_path": "./conversation.json"
}
# from zhipuai import ZhipuAI
# # chatbot = ZhipuAI(config)
# chatbot = OpenAIChat(config)

'''
定义后端路由
路由是客户端（如浏览器）与服务器交互的入口点。通过 Flask 提供的 @app.route() 装饰器，你可以定义 URL 及其对应的处理逻辑。
@app.route("/") 指定了 URL / 的处理逻辑。
render_template() 函数会查找 templates 文件夹中的 chat.html，将它渲染并返回给浏览器。
'''
@app.route("/")
def index():
    """返回聊天框界面"""
    return render_template("chat.html")  # 需要一个 chat.html 前端文件

'''
API 数据路由：
定义了 /chat 路由，用于处理前端发送的聊天请求。
使用 request.json.get() 解析前端发送的数据。
调用聊天机器人的方法，并通过 jsonify() 返回数据。
'''


# FILE_PATH = "./conversation.json"

class ChatNode():
    """chat节点
    """
    def __init__(self, config: dict):
        """初始化
        Args:
            config  app参数配置信息
        """
        self.chat_config = config
        # self.res = None
        self.chat = OpenAIChat(self.chat_config)

        ## 本轮聊天ID
        self.chat_id = 0
        ## 取消的聊天ID
        self.cancel_chat_id = -1
        try:
            with open(self.chat_config['file_path'], "x", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        except FileExistsError:
            pass # 如果文件已存在，则无需初始化
    '''
    def keyboard_control(self):
        """control task.
        """
        if self.keyboard.kbhit():
            key_value = ord(self.keyboard.getch())
            if key_value == ord('q'): 
                logger.info('keyboard exit.')
                self.close()
    '''
    
    # def create_answer_msg(self, msg: dict, chat_id: int):
    #     """创建聊天响应消息
    #     Args:
    #         msg, 聊天响应消息
    #     """
    #     data_obj = {
    #         'node': "chat",
    #         'topic': "chat/answer",
    #         'type': "json",
    #         'data':{
    #             'chat_id': chat_id,
    #             'seq': msg['seq'],
    #             'text': msg['text'],
    #         }    
    #     }
    #     return data_obj

    # def __initialize_conversation_file__(self):
    #     try:
    #         with open(FILE_PATH, "x", encoding="utf-8") as f:
    #             json.dump([], f, ensure_ascii=False, indent=4)
    #     except FileExistsError:
    #         pass # 如果文件已存在，则无需初始化

    # 添加一条对话记录     
    def add_conversation(self, text: str, bot_res):
        # 获取当前时间戳
        time_stamp = time.time()
        # 读取现有记录
        with open(self.chat_config['file_path'], "r", encoding="utf-8") as f:
            conversations = json.load(f)
        if bot_res:
            data_obj = {
                    'time_stamp': time_stamp,
                    'bot_text': text
            }
        else:
            data_obj = {
                    'time_stamp': time_stamp,
                    'user_text': text
            }
        # 添加新记录
        conversations.append(data_obj)
        # 将更新后的记录写回文件
        with open(self.chat_config['file_path'], "w", encoding="utf-8") as f:
            json.dump(conversations, f, ensure_ascii=False, indent=4)

    def handle_mq_msg(self, msg, stream=True):
        """mq 消息处理, 根据请求执行相应操作
        Args: 
            msg  从订阅节点接收到的消息
            stream 是否启动流失响应
        TODO: 增加聊天打断检测
        """
        # print(f"msg is: {msg}")
        logger.debug("got msg: {}".format(msg))
        # topic = msg['topic']
        # text = msg['data']['text']
        # if topic == 'request/cancel':
        #     self.cancel_chat_id = msg['data']['chat_id']
        #     logger.info('receive cancel signal,current chat_id: {}, cancel chat_id: {}'.format(self.chat_id, self.cancel_chat_id))

        # elif topic == 'asr/response':
        #     logger.debug(msg)
        #     text = msg['data']['text']
        #     self.chat_id = msg['data']['chat_id']
        #     logger.info('user: {}'.format(text))

        #     ## 判断是否为取消的ID,如果是则不进行chat请求
        #     if self.chat_id <= self.cancel_chat_id:
        #         logger.info('this chat already cancel, chat_id: {}, cancel chat_id: {}'.format(self.chat_id, self.cancel_chat_id))
        #         return

        if stream:
            ## 流式对话
            bot_list = []
            reponse = self.chat.get_response_stream(msg)
            # print(f"response: {reponse['text']}")
            for chunk in reponse:
                # print(f"chunka: {chunk}")
                answer_msg = self.chat.decode_chunk(chunk)
                # print(f"chunkb: {answer_msg}")
                if answer_msg is not None:
                    logger.info("{:2} {}".format(answer_msg['seq'], answer_msg['text']))
                    
                    # self.auto_send(self.create_answer_msg(answer_msg, self.chat_id))
                    
                    bot_list.append(answer_msg)  # 将 chunk 添加到列表
            # print(f"bot_list: {bot_list[0]['text']}")
            # bot_text = ''.join(bot_list[0]['text']) # 将列表字符串拼接为一个整体
            print(f"bot_text: {bot_list[0]['text']}")
            self.add_conversation(bot_list[0]['text'], True) # 将bot回复保存到另一个json文件中
            return answer_msg['text']
        else:
            answer_msg = self.chat.get_response(msg)
            logger.info("{:2} {}".format(answer_msg['seq'], answer_msg['text']))
            # self.auto_send(self.create_answer_msg(answer_msg, self.chat_id))
            self.add_conversation(answer_msg, True) # 将bot回复保存到另一个json文件中
            return answer_msg['text']

    def shandle_mq_msg(self, msg, stream=True):
        """mq 消息处理, 根据请求执行相应操作
        Args: 
            msg  从订阅节点接收到的消息
            stream 是否启动流失响应
        TODO: 增加聊天打断检测
        """
        # print(f"msg is: {msg}")
        logger.debug("got msg: {}".format(msg))
        # topic = msg['topic']
        # text = msg['data']['text']
        # if topic == 'request/cancel':
        #     self.cancel_chat_id = msg['data']['chat_id']
        #     logger.info('receive cancel signal,current chat_id: {}, cancel chat_id: {}'.format(self.chat_id, self.cancel_chat_id))

        # elif topic == 'asr/response':
        #     logger.debug(msg)
        #     text = msg['data']['text']
        #     self.chat_id = msg['data']['chat_id']
        #     logger.info('user: {}'.format(text))

        #     ## 判断是否为取消的ID,如果是则不进行chat请求
        #     if self.chat_id <= self.cancel_chat_id:
        #         logger.info('this chat already cancel, chat_id: {}, cancel chat_id: {}'.format(self.chat_id, self.cancel_chat_id))
        #         return
        # print("steam: ", stream)
        if stream:
            ## 流式对话
            bot_list = []
            reponse = self.chat.get_response_stream(msg)
            # print(f"response: {reponse}")
            for chunk in reponse:
                # print(f"chunka: {chunk}")
                answer_msg = self.chat.sdecode_chunk(chunk, socketio)
                # print(answer_msg)
                # if answer_msg is not None:
                    # socketio.emit('test', answer_msg)
                # emit('test', answer_msg)
                # socketio.emit('test', answer_msg)
                # print(f"msg: {answer_msg}")
                # for i in self.chat.sdecode_chunk(chunk):
                    # socketio.emit('response', i)
                    # print(i)
                # print(f"chunkb: {answer_msg}")
                if answer_msg is not None:
                    logger.info("{:2} {}".format(answer_msg['seq'], answer_msg['text']))
                    # return answer_msg['text']
                    # self.auto_send(self.create_answer_msg(answer_msg, self.chat_id))
                    
                    bot_list.append(answer_msg)  # 将 chunk 添加到列表
            # print(f"bot_list: {bot_list}")
            # bot_text = ''.join(bot_list) # 将列表字符串拼接为一个整体
            # print(f"bot_text: {bot_text}")
            # self.add_conversation(bot_text) # 将bot回复保存到另一个json文件中
            print(f"bot_text: {bot_list[0]['text']}")
            self.add_conversation(bot_list[0]['text'], True) # 将bot回复以字符串保存到另一个json文件中
            return answer_msg['text']
                    
        else:
            answer_msg = self.chat.get_response(msg)
            logger.info("{:2} {}".format(answer_msg['seq'], answer_msg['text']))
            # self.auto_send(self.create_answer_msg(answer_msg, self.chat_id))
            self.add_conversation(answer_msg, True) # 将bot回复保存到另一个json文件中    
            return answer_msg['text']           


    def launch(self):
        """循环任务
        """
        ## 启动rabitmq transport线程
        # self.transport_start()
        
        # while not self.node_exit:
        #     sleep(0.001)
        #     # self.keyboard_control()
        #     ## 读取rabitmq数据
        # mq_msg = self.auto_read()
        #     if mq_msg is not None:
        self.user_message = request.json.get("message", "").strip()
        
        
        print(f"user_message : {self.user_message}")
        if not self.user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        try:
            self.add_conversation(self.user_message, False) #将用户输出记录
            response = self.handle_mq_msg(self.user_message)
            # print(f"bot_message : {response}")
            # 调用 OpenAIChat 实例的 chat 方法
            # response = self.chat(self.user_message)
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    def slaunch(self, data):
        """循环任务
        """
        ## 启动rabitmq transport线程
        # self.transport_start()
        
        # while not self.node_exit:
        #     sleep(0.001)
        #     # self.keyboard_control()
        #     ## 读取rabitmq数据
        # mq_msg = self.auto_read()
        #     if mq_msg is not None:
        # self.user_message = request.json.get("message", "").strip()
        self.user_message = data
        print(f"user_message : {self.user_message}")
        if not self.user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        try:
            self.add_conversation(self.user_message, False) #将用户输出记录
            response = self.shandle_mq_msg(self.user_message)
            # print(f"bot_message : {response}")
            # 调用 OpenAIChat 实例的 chat 方法
            # response = self.chat(self.user_message)
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# def main(config: dict):
#     """入口函数
#     """
#     chat_node = ChatNode(config)
#     return(chat_node.launch())

@app.route("/chat", methods=["POST"])
def chat():
    chat_node = ChatNode(config)
    # main()
    return(chat_node.launch())

@socketio.on('start_stream')
def handle_start_stream(data):
    
    print(data)
    # data = json.loads(data['message'])
    
    chat_node = ChatNode(config)
    chat_node.slaunch(data["message"])
    # def generate_stream():
    #     for i in range(10):  # 模拟流式输出，每秒发送一次数据
    #         time.sleep(1)
    #         data = f"Data chunk {i+1}"
    #         emit('stream_data', data)  # 发送数据到客户端
    #         print(f"Sent: {data}")

    # 启动流式输出
    # generate_stream()
    # """处理聊天请求"""
    # user_message = request.json.get("message", "").strip()
    # if not user_message:
    #     return jsonify({"error": "Message cannot be empty"}), 400

    # try:
    #     # 调用 OpenAIChat 实例的 chat 方法
    #     response = chatbot.chat(user_message)
    #     return jsonify({"response": response})
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

# socketio_server = SocketIO(app)

if __name__ == "__main__":
    logger.info("main app start...")
    socketio.run(app, debug=True, host='0.0.0.0') # 让你的 Flask 应用运行在一个本地开发服务器上。提供自动重载功能和详细的错误页面，帮助开发者快速调试代码。

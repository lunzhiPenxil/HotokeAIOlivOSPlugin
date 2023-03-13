import OlivOS
import HotokeAIOlivOSPlugin

import urllib
import requests
import json
import traceback
import re

global_Proc = None

def logProc(Proc, level, message, segment):
    Proc.log(
        log_level = level,
        log_message = message,
        log_segment = segment
    )

def globalLog(level, message, segment):
    if HotokeAIOlivOSPlugin.main.global_Proc != None:
        logProc(HotokeAIOlivOSPlugin.main.global_Proc, level, message, segment)

class Event(object):
    def init(plugin_event, Proc):
        global global_Proc
        global_Proc = Proc

    def private_message(plugin_event, Proc):
        unity_message(plugin_event, Proc)

    def group_message(plugin_event, Proc):
        unity_message(plugin_event, Proc)

def unity_message(plugin_event:OlivOS.API.Event, Proc:OlivOS.pluginAPI.shallow):
    messageObj = OlivOS.messageAPI.Message_templet(
        'olivos_string',
        plugin_event.data.message
    )
    message = ''
    for messageObj_this in messageObj.data:
        if type(messageObj_this) is OlivOS.messageAPI.PARA.text:
            message += messageObj_this.OP()
    if message.lower().startswith('.hotoke') \
    or message.lower().startswith('。hotoke') \
    or message.lower().startswith('/hotoke') \
    or message.lower().startswith('救命'):
        if message.lower().startswith('.hotoke'):
            message = message.lstrip('.hotoke')
        elif message.lower().startswith('。hotoke'):
            message = message.lstrip('。hotoke')
        elif message.lower().startswith('/hotoke'):
            message = message.lstrip('/hotoke')
        elif message.lower().startswith('救命'):
            message = message.lstrip('救命')
        message = message.lstrip(' ')
        if len(message) > 0:
            res = getHotokeAI(message, 'zh')
            resAn = None
            if res != None:
                try:
                    resAn = res['note']
                except Exception as e:
                    traceback.print_exc()
                    resAn = None
            if resAn == None:
                resAn = '冥想中断了！别担心，机械佛稍后会回答您的问题，人工智能始终与您相伴~'
            else:
                resAn = re.sub(r'\<br[^\<]*/\>', '\n', resAn)
                resAn = re.sub(r'\<p[^\<]+\>.+\</p[^\<]*\>', '', resAn)
                resAn = re.sub(r'\<[^\<]+\>', '', resAn)
                resAn = re.sub(r'\n+', '\n', resAn)
            plugin_event.reply(resAn)

def getHotokeAI(onayami:str, la:str = 'zh'):
    res = GETHttpJson2Dict(
        'https://hotoke.ai/gen.php',
        {
            'onayami': onayami,
            'la': la
        }
    )
    return res


def GETHttpJson2Dict(url:str, payload:dict):
    msg_res = None
    res = None
    send_url = url
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'OlivOS/HotokeAI.plugin'
    }
    try:
        msg_res = requests.request(
            "POST",
            send_url,
            headers=headers,
            data=payload,
            timeout=180,
            proxies=OlivOS.webTool.get_system_proxy()
        )
        res = json.loads(msg_res.text)
    except Exception as e:
        traceback.print_exc()
        res = None
    return res

def get_system_proxy():
    res = urllib.request.getproxies()
    for res_this in res:
        res[res_this] = res[res_this].lstrip('%s://' % res_this)
    return res


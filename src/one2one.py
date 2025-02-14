import common
from langdetect import detect
from nostrclient.relay_pool import RelayPool
from nostrclient.log import log
from nostrclient.key import PrivateKey,PublicKey
from nostrclient.localStorage import local_storage
from nostrclient.actions import like_event
from nostrclient.key import PublicKey
from nostrclient.nip19 import encode_bech32
from nostrclient import bech32
from nostrclient import nip44
from nostrclient.event import Event
import db
import dmevent 
import queue
import json
import time
taskevent = queue.Queue()

import os
import signal
import sys
 
log.blue("程序开始启动")
# 定义信号处理函数，用于重启程序
def restart_program(signum, frame):
    os.execv(sys.executable, [sys.executable] + sys.argv)


signal.signal(signal.SIGALRM, restart_program)
signal.alarm(300)

from config import relays 


nkeylist = db.find_newkey()
plist = []
for i in nkeylist:
    plist.append(i[2])

filters    = {"kinds":[4,1059], "#p": plist,"limit":10}


r = RelayPool(relays)

r.connect(5)

def find_key_by_tags(tags):
    for tag  in tags:
        if tag[0] == 'p':
            return tag[1]
    return None 

def forward_message(nkey,event14):
    srcpubkey = event14['pubkey']
    content   = event14['content']

    relay = db.get_relay(str(nkey.public_key))
    if not relay:
        return 

    if srcpubkey == relay[2]:
        pubkey = relay[3]
    else:
        pubkey = relay[2]
     
    # 匿名发送
    n1key = PrivateKey() 
    event1059 = dmevent.dmEvent(nkey,pubkey,content,n1key)

    for r1 in r.RelayList:
        r1.Privkey = n1key
    r.Privkey = n1key 
    r.publish(event1059)

def one2one(e):
    if db.get_one2one(e['id']):
        return 
    db.create_one2one(e['id'])
    
    if e['kind'] == 4:
      content = nip04.decrypt(e['content'],pkey.raw_secret, e['pubkey'])
      relay_key = find_key_by_tags(e['tags'])
      if relay_key is None:
        return 
      e['content'] = content
      print("收到一个信息:",e['id'],"转发到",e['tags'],) 
      forward_message(nkey,e)

    elif e['kind'] == 1059:
      relay_key = find_key_by_tags(e['tags'])
      if relay_key is None:
        return 
      result = db.get_newkey(relay_key)
      privkey = result[1]
      nkey = PrivateKey(bytes.fromhex(privkey))

      content,pubkey = dmevent.decrypt_1059(e,nkey)
      event14 = json.loads(content)
      print("收到一个信息:",e['id'],"转发到",e['tags'],)
      forward_message(nkey,event14)

       

def handler_event(e):
     
    if e['kind'] == 4 or e['kind'] == 1059:
        taskevent.put(e)

subs = r.subscribe (filters)
subs.on("EVENT",handler_event)

while True:  # 死循环
    event = taskevent.get()
    one2one(event)
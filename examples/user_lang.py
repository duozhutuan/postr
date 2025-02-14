import common
from langdetect import detect
from nostrclient.relay_pool import RelayPool
from nostrclient.log import log
from nostrclient.key import PrivateKey
from nostrclient.localStorage import local_storage
from nostrclient.actions import like_event
from nostrclient.key import PublicKey
from nostrclient.nip19 import encode_bech32
from nostrclient import bech32
import db
import queue
user_queue = queue.Queue()


Keypriv = local_storage.get("Keyprivpost")
pkey = PrivateKey(Keypriv)
print("Your public key: ",pkey.public_key)
print("Your public key bech32: ",pkey.public_key.bech32())

relayServer =  [ 
  'wss://nostr-01.yakihonne.com', 
  'wss://relay.damus.io',
  'wss://nos.lol',
] 

hub = "wss://bridge.duozhutuan.com/";
hub = "";

relays = [hub + relay for relay in relayServer]
filters    = {"kinds":[1],"limit":10}


r = RelayPool(relays)

r.connect(5)

def detect_lang(text):
    try:
        return detect(text)
    except:
        return None

def handler_event(event):
    lang = detect_lang(event['content'])
    if lang:
        user_queue.put((event['pubkey'],lang))
subs = r.subscribe(filters)
subs.on("EVENT",handler_event)

while True:  # 死循环
        pubkey,lang = user_queue.get()
        print(pubkey,lang)
        if not db.get_user(pubkey):
            db.create_user(pubkey,lang,"")

import time
import json 
from nostrclient.event import Event 
from nostrclient import nip44 

def dmEvent(nkey,pubkey,content,n1key):
  event14 = {
    "kind":14,
    "pubkey":str(nkey.public_key),
    "tags":[["p",pubkey]],
    "content":content,
    "created_at":int(time.time())
  }
  event14id = Event.compute_id(
    event14['pubkey'],
    event14['created_at'],
    event14['kind'],
    event14['tags'],
    event14['content'],
  )

  event14['id'] = event14id
  conversation_key = nip44.get_conversation_key(nkey.raw_secret,pubkey)

  event13 = {
    "kind":13,
    "pubkey":str(nkey.public_key),
    "created_at":int(time.time()),
    "content":nip44.encrypt(json.dumps(event14),conversation_key),
    "tags":[],
  }
  event13id = Event.compute_id(
    event13['pubkey'],
    event13['created_at'],
    event13['kind'],
    event13['tags'],
    event13['content'],
  )

  sig = nkey.sign_message_hash(bytes.fromhex(event13id))
  event13['id'] = event13id
  event13['sig'] = sig

  conversation_key1 = nip44.get_conversation_key(n1key.raw_secret,pubkey)
  event1059 = {
    "kind":1059,
    "tags": [
    ["p", pubkey ] ],
    "content":nip44.encrypt(json.dumps(event13),conversation_key1),
  }

  return event1059 


def decrypt_1059(e,nkey):
    # 匿名 pubkey
    conversation_key = nip44.get_conversation_key(nkey.raw_secret, e['pubkey'])

    encrypt_event = json.loads(nip44.decrypt(e['content'],conversation_key))
    if encrypt_event['kind'] == 13:
        # 真实的 pubkey 发送者的 
        conversation_key = nip44.get_conversation_key(nkey.raw_secret, encrypt_event['pubkey'])
        content = nip44.decrypt(encrypt_event['content'],conversation_key)

        return content,encrypt_event['pubkey']

    return None,None 
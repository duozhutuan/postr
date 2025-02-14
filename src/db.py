import sqlite3
# 连接到数据库（如果文件不存在，则会创建）
conn = sqlite3.connect('postr.db')
cursor = conn.cursor()

# 中转 关系表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS relay_service (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        relay_key TEXT NOT NULL,         -- 中转服务的标识符
        client1_pubkey TEXT NOT NULL,   -- 客户1的公钥
        client2_pubkey TEXT NOT NULL    -- 客户2的公钥
    )
''')

# 用户语言信息表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pubkey TEXT NOT NULL UNIQUE,   -- 用户的公钥，唯一标识
        language TEXT NOT NULL,        -- 用户的语言信息
        name TEXT                      -- 用户的昵称，可以为空
    )
''')


# postr 事件处理状态 表
# status 
# 1,开始联系一个新用户
# 2,用户已经回馈,对接完成


cursor.execute('''
    CREATE TABLE IF NOT EXISTS eventid (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eventid TEXT NOT NULL,          
        status  TEXT
    )
''')

# 中转人 密钥表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS newkey (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        privkey  TEXT NOT NULL,          
        pubkey   TEXT
    )
''')

#
# 中转人处理 eventid 完成表
#
cursor.execute('''
    CREATE TABLE IF NOT EXISTS one2one (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eventid TEXT NOT NULL,          
        status  TEXT
    )
''')

def create_user(pubkey,lang,name):
    cursor.execute('''
    INSERT INTO user_info (pubkey, language, name)
    VALUES (?, ?, ?)
    ''', (pubkey, lang, name))  # 英语用户，昵称为 Alice

    conn.commit()

def get_user(pubkey):
    cursor.execute('''
    SELECT * FROM user_info WHERE pubkey = ?
    ''', (pubkey,))
    result = cursor.fetchone()
    return result

def get_random_user(lang):
    cursor.execute("SELECT * FROM user_info WHERE language = ?  ORDER BY RANDOM() LIMIT 1",
    (lang,))
    result = cursor.fetchone()
    if result :
        return result 

    cursor.execute("SELECT * FROM user_info   ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    return result 

def create_relay(pubkey,client1,client2):
    cursor.execute('''
    INSERT INTO relay_service (relay_key, client1_pubkey, client2_pubkey)
    VALUES (?, ?, ?)
    ''', (str(pubkey), client1, client2))  

    conn.commit()

def get_relay(pubkey):
    cursor.execute('''
    SELECT * FROM relay_service WHERE relay_key = ?
    ''', (pubkey,))
    result = cursor.fetchone()
    return result

def create_event(eventid):
    cursor.execute('''
    INSERT INTO eventid (eventid, status)
    VALUES (?, ?)
    ''', (eventid, 1, ))  

    conn.commit()

def get_event(eventid):
    cursor.execute('''
    SELECT * FROM eventid WHERE eventid = ?
    ''', (eventid,))
    result = cursor.fetchone()
    return result

def update_event(eventid,status=2):
    update_query = "UPDATE eventid SET status = ? WHERE eventid = ?"
    cursor.execute(update_query, (status, eventid))
    conn.commit()

def create_newkey(nkey):
    cursor.execute('''
    INSERT INTO newkey (privkey, pubkey)
    VALUES (?, ?)
    ''', (str(nkey), str(nkey.public_key), ))  
    conn.commit()    


def get_newkey(pubkey):
    cursor.execute('''
    SELECT * FROM newkey WHERE pubkey = ?
    ''', (pubkey,))
    result = cursor.fetchone()
    return result    

def find_newkey(count=100,offset=0):
    cursor.execute('''
    SELECT * FROM newkey LIMIT? OFFSET?
    ''', (count,offset,))
    result = cursor.fetchall()
    return result  

def create_one2one(eventid):
    cursor.execute('''
    INSERT INTO one2one (eventid)
    VALUES (?)
    ''', (eventid,))  
    conn.commit()    

def get_one2one(eventid):
    cursor.execute('''
    SELECT * FROM one2one WHERE eventid = ?
    ''', (eventid,))
    result = cursor.fetchone()
    return result  
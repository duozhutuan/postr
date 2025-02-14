relayServer =  [ 
  'wss://nostr-01.yakihonne.com', 
  'wss://relay.damus.io',
  'wss://nos.lol',
] 

hub = "wss://bridge.duozhutuan.com/";
hub = "";

relays = [hub + relay for relay in relayServer]
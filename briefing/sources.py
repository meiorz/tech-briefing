from briefing.models import Feed

RSS_FEEDS = [
    Feed("krebs", "Krebs on Security", "security", "https://krebsonsecurity.com/feed/"),
    Feed("thn", "The Hacker News", "security", "https://feeds.feedburner.com/TheHackersNews"),
    Feed("bleeping", "BleepingComputer", "security", "https://www.bleepingcomputer.com/feed/"),
    Feed("schneier", "Schneier on Security", "security", "https://www.schneier.com/feed/atom/"),
    Feed("darkreading", "Dark Reading", "security", "https://www.darkreading.com/rss.xml"),
    Feed("coindesk", "CoinDesk", "crypto", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    Feed("cointelegraph", "Cointelegraph", "crypto", "https://cointelegraph.com/rss"),
    Feed("cryptoslate", "CryptoSlate", "crypto", "https://cryptoslate.com/feed/"),
    Feed("bitcoincom", "Bitcoin.com News", "crypto", "https://news.bitcoin.com/feed/"),
]

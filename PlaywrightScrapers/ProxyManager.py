
available_proxies = [
    "185.164.138.104:1080",
]

used_proxies = [

]

def get_next_proxy():
    if not available_proxies:
        return None

    proxy = mark_used()
    return proxy

def mark_used():
    if not available_proxies:
        return None

    current_proxy = available_proxies.pop(0)
    used_proxies.append(current_proxy)
    return current_proxy

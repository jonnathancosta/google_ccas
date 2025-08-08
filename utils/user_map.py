user_chat_map = {}
 
def get_user_status(identifier):
    user_info = user_chat_map.get(identifier, {})
    return user_info.get("status", "bot")

def set_user_status(identifier, status):
    if identifier in user_chat_map:
        user_chat_map[identifier]["status"] = status
    else:
        user_chat_map[identifier] = {"status": status}

def is_escalated(identifier):
    return get_user_status(identifier) == "escalated"

def find_identifier_by_chat_id(chat_id):
    for identifier, info in user_chat_map.items():
        if isinstance(info, dict) and info.get("chat_id") == chat_id:
            return identifier
        elif info == chat_id:
            return identifier
    return None

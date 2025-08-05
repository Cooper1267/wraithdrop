COMMAND_QUEUE = {}

def get(client_id):
    if client_id in COMMAND_QUEUE and COMMAND_QUEUE[client_id]:
        return COMMAND_QUEUE[client_id].pop(0)
    return None


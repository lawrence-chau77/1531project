from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store, is_global_owner
from datetime import datetime, timedelta
import threading
import time

def standup_start_v1(token, channel_id, length):
    store = data_store.get()

    # check valid token 
    auth_user_id = validate_token(token)['user_id']
    # check valid channel id
    if channel_id not in filter_data_store(store_list='channels',key='id'):
        raise InputError(description="Invalid channel_id")
    # check is a member of channel 
    channel_dict = filter_data_store(store_list='channels',key='id',value=channel_id)[0]
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")
    # check if length is negative integer
    if length < 0:
        raise InputError(description="Length cannot be negative integer")
    # check if already an active standup
    if channel_dict['standup_active'] == True:
        raise InputError(description="Already an active standup")
    # set standup to be True 
    channel_dict['standup_active'] == True
    # calculate time_finish
    time_finish = int(datetime.utcnow()+ timedelta(seconds=length).timestamp())
    # threading after length set standup to be False 
    t = threading.Timer(legnth, standup_end(channel_dict, auth_user_id, time_finish))
    t.start()
    # return time_finish
    return time_finish

def standup_end(channel_dict, auth_user_id, time_finish):
    store = data_store.get()
    # send combined message
    standup_str = "\n".join(channel_dict['standup_messages'])
    standup_message = {
        'message_id': len(store['messages']) + len(store['removed_messages']) + 1,
        'u_id': auth_user_id,
        'message': standup_str,
        'time_created': time_finish
    }
    message_store = {
        'message': standup_message,
        'channel_id': channel_dict['id']
    }
    channel_dict['messages'].insert(0, standup_message)
    store['messages'].insert(0, message_store)
    # set standup_active to False
    channel_dict['standup_active'] == False
import pytest
import requests
from src import config 
from src.error import AccessError, InputError
from datetime import datetime, timedelta

@pytest.fixture 
def clear_and_register_channel():
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes@yes.com", 
        'password': "aaaaaa", 
        'name_first': "firstname", 
        "name_last": "lastname"
    })
    register_data = register.json()
    token = register_data['token']

    channel_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token, 
        'name': 'name', 
        'is_public': True
    })
    channel_create_data = channel_create.json()
    channel_id = channel_create_data['channel_id']

    return {
        'token': token, 
        'u_id': register_data['auth_user_id'], 
        'channel_id': channel_id
        }

def test_standup_active_sucess(clear_and_register_channel):
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    requests.post(config.url + 'standup/start/v1',json={
        'token': token,
        'channel_id': channel_id,
        'length': 60,
    })
    cur_time = datetime.utcnow()
    time_finish = int((cur_time + timedelta(seconds = 60)).timestamp())

    standup_active = requests.post(config.url + 'standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    }).json()
    assert standup_active['is_active'] == True
    assert standup_active['time_finish'] == time_finish

def test_no_standup_active_success(clear_and_register_channel):
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    standup_active = requests.post(config.url + 'standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    }).json()
    assert standup_active['is_active'] == False
    assert standup_active['time_finish'] == None

def test_invalid_channel(clear_and_register_channel):
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    standup_active = requests.post(config.url + 'standup/active/v1', json={
            'token': token,
            'channel_id': channel_id + 1
        }).json()
    assert standup_active.status_code == InputError.code

def test_not_a_member(clear_and_register_channel):
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    token_2 = register_2_data['token']

    standup_active = requests.post(config.url + 'standup/active/v1', json={
            'token': token_2,
            'channel_id': channel_id
        }).json()
    assert standup_active.status_code == AccessError.code

def test_invalid_token_valid_channel():
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes@yes.com", 
        'password': "aaaaaa", 
        'name_first': "firstname", 
        "name_last": "lastname"
    })
    register_data = register.json()
    token = register_data['token']

    channel_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token, 
        'name': 'name', 
        'is_public': True
    })
    channel_create_data = channel_create.json()
    channel_id = channel_create_data['channel_id']

    standup_active = requests.post(config.url + 'standup/active/v1', json={
            'token': 1,
            'channel_id': channel_id
        }).json()
    assert standup_active.status_code == AccessError.code
    

def test_invalid_token_invalid_channel():
    requests.delete(config.url + 'clear/v1')
    standup_active = requests.post(config.url + 'standup/active/v1', json={
            'token': 1,
            'channel_id': 1
        }).json()
    assert standup_active.status_code == AccessError.code
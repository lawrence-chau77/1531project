import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

'''
channel_leave_v1_test.py: All functions relating to testing the function channel_leave_v1
'''
@pytest.fixture
def clear_and_register():
    '''
    clears then registers a user
    The user creates a channel as well 
    '''
    # clear then register a user 
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes@yes.com", 
        'password': "aaaaaa", 
        'name_first': "firstname", 
        "name_last": "lastname"
    })
    register_data = register.json()
    token = register_data['token']
    # create a channel and get its channel id
    channel_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token, 
        'name': "name", 
        'is_public': True
    })
    channel_create_data = channel_create.json()
    channel_create_data["channel_id"]

    return {
        'token': register_data["token"], 
        'channel_id': channel_create_data["channel_id"], 
        'auth_user_id': register_data['auth_user_id']
        }

def test_valid_channel_authorised_owner(clear_and_register):
    '''
    Testing success case
    '''
    token = clear_and_register['token']
    channel_id = clear_and_register['channel_id']
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    }).json()
    token_2 = register['token']
    id_num_2 = register['auth_user_id']
    requests.post(config.url + 'channel/invite/v2', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': id_num_2
    })
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={
        'token': token, 
        'channel_id': channel_id
    })
    channel_leave_data = channel_leave.json()

    assert channel_leave_data == {}
    channel_details = requests.get(config.url + 'channel/details/v2', params={
        'token': token_2, 
        'channel_id': channel_id
    }).json()
    url_one_data = requests.get(config.url + 'user/profile/v1', params={
        'token': token_2,
        'u_id': id_num_2 
    }).json()
    url_one = url_one_data['user']['profile_img_url']
    assert channel_details == {
        'name': 'name',
        'is_public': True,
        'owner_members': [], 
        'all_members': [
            {
                'u_id': id_num_2,
                'email': 'yes2@yes.com',
                'name_first': 'name' ,
                'name_last': 'name',
                'handle_str': 'namename',
                'profile_img_url': url_one
            }
        ],

    }

def test_valid_channel_authorised_member(clear_and_register):
    '''
    Testing success case and there exists a user who isn't part of the channel 
    '''
    token = clear_and_register['token']
    channel_id = clear_and_register['channel_id']
    id_num = clear_and_register['auth_user_id']
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    }).json()
    token_2 = register['token']
    id_num_2 = register['auth_user_id']
    requests.post(config.url + 'channel/invite/v2', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': id_num_2
    })
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={'token': token_2, 'channel_id': channel_id})
    channel_leave_data = channel_leave.json()

    assert channel_leave_data == {}
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id}).json()
    url_one_data = requests.get(config.url + 'user/profile/v1', params={
        'token': token,
        'u_id': id_num 
    }).json()
    url_one = url_one_data['user']['profile_img_url']
    assert channel_details == {
        'name': 'name',
        'is_public': True,
        'owner_members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
                'profile_img_url': url_one
            }
        ],
        'all_members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
                'profile_img_url': url_one
            }
        ],
    }

def test_valid_channel_unauthorised(clear_and_register):
    '''
    Testing case where non-member of channel calls function 
    '''
    channel_id = clear_and_register['channel_id']
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_data = register.json()
    token_2 = register_data['token']
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={'token': token_2, 'channel_id': channel_id})
    assert channel_leave.status_code == AccessError.code

def test_valid_channel_invalid_token(clear_and_register):
    '''
    Testing a valid channel called by an invalid token
    '''
    channel_id = clear_and_register['channel_id']
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={'token': "", 'channel_id': channel_id})
    assert channel_leave.status_code == AccessError.code

def test_invalid_channel_valid_token():
    '''
    testing an invalid channel called by valid token
    '''
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes@yes.com", 
        'password': "aaaaaa", 
        'name_first': "firstname", 
        "name_last": "lastname"
    })
    register_data = register.json()
    token = register_data['token']
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={'token': token, 'channel_id': 1})
    assert channel_leave.status_code == InputError.code

def test_invalid_channel_invalid_token():
    '''
    testing an invalid channel called by invalid token
    '''
    requests.delete(config.url + 'clear/v1')
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={'token': 1, 'channel_id': 1})
    assert channel_leave.status_code == AccessError.code

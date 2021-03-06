import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

'''
channel_addowner_v1_test.py: All functions related to testing the channel_addowner_v1 function
'''
@pytest.fixture
def clear_and_channel_2_members():
    '''
    clears and then registers two users 
    Creates a channel with the two users 
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

    channel_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token, 
        'name': 'name', 
        'is_public': True
    })
    channel_create_data = channel_create.json()
    channel_id = channel_create_data['channel_id']

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    u_id_2 = register_2_data['auth_user_id']

    requests.post(config.url + 'channel/invite/v2', json ={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': u_id_2
    })
    

    return {
        'token': token, 
        'token_2': register_2_data['token'], 
        'u_id': register_data['auth_user_id'], 
        'u_id_2': u_id_2, 
        'channel_id': channel_id
        }


def test_valid_channel_channel_owner(clear_and_channel_2_members):
    '''
    when token is valid, channel is valid, called by a channel owner 
    '''
    token = clear_and_channel_2_members['token']
    token_2 = clear_and_channel_2_members['token_2']
    u_id = clear_and_channel_2_members['u_id']
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']

    requests.post(config.url + 'channel/addowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': u_id_2
    })
    channel_details = requests.get(config.url + 'channel/details/v2', params={
        'token': token, 
        'channel_id': channel_id
    })
    channel_details_data = channel_details.json()
    url_one_data = requests.get(config.url + 'user/profile/v1', params={
        'token': token,
        'u_id': u_id
    }).json()
    url_one = url_one_data['user']['profile_img_url']
    url_two_data = requests.get(config.url + 'user/profile/v1', params={
        'token': token_2,
        'u_id': u_id_2
    }).json()
    url_two = url_two_data['user']['profile_img_url']
    assert channel_details_data['owner_members'] == [
            {
                'u_id': u_id,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
                'profile_img_url': url_one
            } ,

            {
                'u_id': u_id_2,
                'email': 'yes2@yes.com',
                'name_first': 'name',
                'name_last': 'name',
                'handle_str': 'namename',
                'profile_img_url': url_two
            }
        ]

def test_nonmember_global_owner():
    '''
    when token is valid, channel is valid and called by global owner who isn't a member
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

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    token_2 = register_2_data['token']

    channel_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token_2, 
        'name': 'name', 
        'is_public': True
    })
    channel_create_data = channel_create.json()
    channel_id = channel_create_data['channel_id']

    register_3 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes3@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_3_data = register_3.json()
    u_id_3 = register_3_data['auth_user_id']

    requests.post(config.url + 'channel/invite/v2', json ={
        'token': token_2, 
        'channel_id': channel_id, 
        'u_id': u_id_3
    })
    
    channel_addowner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': u_id_3
    })
    assert channel_addowner.status_code == AccessError.code

def test_invalid_channel():
    '''
    when token is valid but channel id is invalid
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
    u_id = register_data['auth_user_id']
    channel_addowner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token, 
        'channel_id': 1, 
        'u_id': u_id
    })
    assert channel_addowner.status_code == InputError.code

def test_invalid_u_id(clear_and_channel_2_members):
    '''
    when token is valid but u_id is invalid
    '''
    token = clear_and_channel_2_members['token']
    u_id = clear_and_channel_2_members['u_id']
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']

    invalid_id = 1
    while (invalid_id == u_id or invalid_id == u_id_2):
        invalid_id += 1

    channel_addowner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': invalid_id
    })
    assert channel_addowner.status_code == InputError.code

def test_invaid_u_id_not_member(clear_and_channel_2_members):
    '''
    when token is valid, channel is valid but user not a member
    '''
    token = clear_and_channel_2_members['token']
    channel_id = clear_and_channel_2_members['channel_id']

    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes3@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_data = register.json()
    not_member_id = register_data['auth_user_id']
    channel_addowner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id':not_member_id
    })
    assert channel_addowner.status_code == InputError.code 
    
def test_invalid_u_id_not_user(clear_and_channel_2_members):
    '''
    when token is valid, channel is valid but user_id not a real user 
    '''
    token = clear_and_channel_2_members['token']
    u_id = clear_and_channel_2_members['u_id']
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']

    invalid_u_id = 1
    while (invalid_u_id == u_id or invalid_u_id == u_id_2):
        invalid_u_id += 1
    channel_addowner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': invalid_u_id
    })
    assert channel_addowner.status_code == InputError.code

def test_already_channel_owner(clear_and_channel_2_members):
    '''
    when token is valid, channel is valid but user_id is already channel owner
    '''
    token = clear_and_channel_2_members['token']
    u_id = clear_and_channel_2_members['u_id']
    channel_id = clear_and_channel_2_members['channel_id']
    channel_addowner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': u_id
    })
    assert channel_addowner.status_code == InputError.code

def test_no_owner_permissions(clear_and_channel_2_members):
    '''
    valid token, valid channel, valid u_id, no owner permissions 
    '''
    token_2 = clear_and_channel_2_members['token_2']
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']
    channel_addowner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': token_2, 
        'channel_id': channel_id, 
        'u_id': u_id_2
    })
    assert channel_addowner.status_code == AccessError.code

def test_invalid_token_valid_channel_valid_u_id(clear_and_channel_2_members):
    '''
    invalid token, valid channel, valid u_id
    '''
    token = clear_and_channel_2_members['token']
    token_2 = clear_and_channel_2_members['token_2']
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']

    invalid_token = 1
    while (invalid_token == token or invalid_token == token_2):
        invalid_token += 1

    channel_addowner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': invalid_token, 
        'channel_id': channel_id, 
        'u_id': u_id_2
    })
    assert channel_addowner.status_code == AccessError.code

def test_no_owner_permissions_invalid_channel(clear_and_channel_2_members):
    '''
    invaid token, invalid channel 
    '''
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']
    
    invalid_channel_id = 1
    while (invalid_channel_id == channel_id):
        invalid_channel_id += 1

    channel_addowner = requests.post(config.url + 'channel/addowner/v1', json={
        'token': "", 
        'channel_id': invalid_channel_id, 
        'u_id': u_id_2
    })
    assert channel_addowner.status_code == AccessError.code

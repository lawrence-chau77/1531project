import pytest
import requests
from src import config
from src.error import AccessError, InputError

'''
users_profile_v1_test.py: All functions related to testing the users_profile_v1 function
'''

# define global variable for default profile_img_url
global DEFAULT_PROFILE_IMG_URL

@pytest.fixture
def clear_and_register_user0():
    '''
    clear and registers first user
    '''
    requests.delete(config.url + 'clear/v1')
    user0_register = {
        'email' : '0000@unsw.edu.au',
        'password' : 'password',
        'name_first' : 'firstname0',
        'name_last' : 'lastname0',
    }
    user0 = requests.post(config.url + 'auth/register/v2', json=user0_register).json()


    # set global variable for default profile_img_url
    global DEFAULT_PROFILE_IMG_URL
    DEFAULT_PROFILE_IMG_URL = requests.get(config.url + 'users/all/v1', params={'token': user0['token']}).json()['users'][0]['profile_img_url']


    return {
        'token_valid': user0['token'],
        'u_id': user0['auth_user_id']
    }


def test_invalid_token_and_invalid_uid(clear_and_register_user0):
    '''
    test invalid token with invalid uid, this should raise AccessError
    '''
    user0 = clear_and_register_user0
    info = {
        'token': user0['token_valid'] + '1',
        'u_id': user0['u_id'] + 1
    }
    assert requests.get(config.url + 'user/profile/v1', params=info).status_code == AccessError.code
    
def test_invaild_token_and_valid_uid(clear_and_register_user0):
    '''
    test invalid token with valid uid, and this should raise AccessError
    '''
    user0 = clear_and_register_user0
    info = {
        'token': user0['token_valid'] + '1',
        'u_id': user0['u_id']
    }
    assert requests.get(config.url + 'user/profile/v1', params=info).status_code == AccessError.code

def test_vaild_token_and_invalid_uid(clear_and_register_user0):
    '''
    test invalid uid and this should raise InputError
    '''
    user0 = clear_and_register_user0
    info = {
        'token': user0['token_valid'],
        'u_id': user0['u_id'] + 1
    }
    assert requests.get(config.url + 'user/profile/v1', params=info).status_code == InputError.code

def test_vaild_token_with_one_user_registered(clear_and_register_user0):
    '''
    test a user with valid token and valid uid
    '''
    user0 = clear_and_register_user0
    info = {
        'token': user0['token_valid'],
        'u_id': user0['u_id']
    }
    assert requests.get(config.url + 'user/profile/v1', params=info).json() == {'user':
        {'u_id': user0['u_id'],
        'email': '0000@unsw.edu.au',
        'name_first': 'firstname0',
        'name_last': 'lastname0',
        'handle_str': 'firstname0lastname0',
        'profile_img_url': DEFAULT_PROFILE_IMG_URL}
    }
    
def test_call_others_uid(clear_and_register_user0):
    '''
    test user with valid token and valid uid, and called by others
    '''
    user0 = clear_and_register_user0
    user1_register = {
        'email' : '0001@unsw.edu.au',
        'password' : 'password',
        'name_first' : 'firstname1',
        'name_last' : 'lastname1',
    }
    user1 = requests.post(config.url + 'auth/register/v2', json=user1_register).json()
    
    info = {
        'token': user1['token'],
        'u_id': user0['u_id']
    }

    assert requests.get(config.url + 'user/profile/v1', params=info).json() == {
        'user': {
            'u_id': user0['u_id'],
            'email': '0000@unsw.edu.au',
            'name_first': 'firstname0',
            'name_last': 'lastname0',
            'handle_str': 'firstname0lastname0',
            'profile_img_url': DEFAULT_PROFILE_IMG_URL
        }
    }


def test_many_vaild_users():
    requests.delete(config.url + 'clear/v1')
    users_register = [
        {   'email' : '0000@unsw.edu.au',
            'password' : 'password',
            'name_first' : 'firstname0',
            'name_last' : 'lastname0',
        }, {'email' : '0001@unsw.edu.au',
            'password' : 'password',
            'name_first' : 'firstname1',
            'name_last' : 'lastname1',
        }, {'email' : '0002@unsw.edu.au',
            'password' : 'password',
            'name_first' : 'firstname2',
            'name_last' : 'lastname2',
        }
    ]
    
    user0 = requests.post(config.url + 'auth/register/v2', json=users_register[0]).json()
    user1 = requests.post(config.url + 'auth/register/v2', json=users_register[1]).json()
    user2 = requests.post(config.url + 'auth/register/v2', json=users_register[2]).json()

    info = {
        'token': user0['token'],
        'u_id': user0['auth_user_id']
    }

    assert requests.get(config.url + 'user/profile/v1', params=info).json() == {
        'user': {
            'u_id': user0['auth_user_id'],
            'email': '0000@unsw.edu.au',
            'name_first': 'firstname0',
            'name_last': 'lastname0',
            'handle_str': 'firstname0lastname0',
            'profile_img_url': DEFAULT_PROFILE_IMG_URL
        }
    }

    info['u_id'] = user1['auth_user_id']
    assert requests.get(config.url + 'user/profile/v1', params=info).json() == {
        'user': {
            'u_id': user1['auth_user_id'],
            'email': '0001@unsw.edu.au',
            'name_first': 'firstname1',
            'name_last': 'lastname1',
            'handle_str': 'firstname1lastname1',
            'profile_img_url': DEFAULT_PROFILE_IMG_URL
        }
    }

    info['token'] = user1['token']
    info['u_id'] = user2['auth_user_id']
    assert requests.get(config.url + 'user/profile/v1', params=info).json() == {
        'user': {
            'u_id': user2['auth_user_id'],
            'email': '0002@unsw.edu.au',
            'name_first': 'firstname2',
            'name_last': 'lastname2',
            'handle_str': 'firstname2lastname2',
            'profile_img_url': DEFAULT_PROFILE_IMG_URL
        }
    }

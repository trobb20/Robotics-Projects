from OnshapeSpikePrime.OnshapePlus import *

def configure_client(api_path, base='https://cad.onshape.com'):
    try:
        access, secret = open(api_path).readlines()
        client = Client(configuration={"base_url": base,
                                    "access_key": access.strip('\n'),
                                    "secret_key": secret})
        print('client configured')
    except Exception as e:
        print(e)
        return

    return client

base = 'https://cad.onshape.com'
url = 'https://cad.onshape.com/documents/e61d2284326681e60c354303/w/06c3440ad86b926c4800c9f0/e/4a24c86674282951b16e2dcf'
client = configure_client('OnshapeSpikePrime/apikeys.txt')

mates = getMates(client, url, base)
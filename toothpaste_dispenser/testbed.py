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

def get_request(client, url: str, base: str, end: str):
    fixed_url = '/api/assemblies/d/did/w/wid/e/eid/'+end
    element = OnshapeElement(url)
    method = 'GET'

    params = {}
    payload = {}
    headers = {'Accept': 'application/vnd.onshape.v2+json',
                'Content-Type': 'application/vnd.onshape.v2+json'}

    fixed_url = fixed_url.replace('did', element.did)
    fixed_url = fixed_url.replace('wid', element.wvmid)
    fixed_url = fixed_url.replace('eid', element.eid)

    print(base + fixed_url)

    response = client.api_client.request(method, url=base + fixed_url, query_params=params, headers=headers, body=payload)

    parsed = json.loads(response.data)
    print(json.dumps(parsed, indent=4, sort_keys=True))
    return parsed

base = 'https://cad.onshape.com'
url = 'https://cad.onshape.com/documents/e61d2284326681e60c354303/w/06c3440ad86b926c4800c9f0/e/a34262dd0483af23abdb4057'
client = configure_client('OnshapeSpikePrime/apikeys.txt')

parsed = massProp(client, url, base)

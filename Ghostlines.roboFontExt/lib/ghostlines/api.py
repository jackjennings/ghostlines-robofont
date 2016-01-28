import requests

from ghostlines import env

class Ghostlines(object):

    def __init__(self, version):
        self.version = version

    def send(self, otf=None, recipients=None):
        if not otf and not recipients:
            return

        url = '{}/api/{}/send'.format(env.api_url, self.version)
        files = {'otf': otf}
        data = {'recipients': recipients}

        return requests.post(url, files=files, data=data)

import requests

from ghostlines import env


class Ghostlines(object):

    def __init__(self, version):
        self.version = version

    def send(self, otf=None, recipients=None, notes=None, designer_email_address=None):
        if not otf and not recipients:
            return

        url = self.path('send')
        files = {'otf': otf}
        data = {
            'recipients': recipients,
            'notes': notes,
            'designer_email_address': designer_email_address
        }

        return requests.post(url, files=files, data=data)

    def enable_applicants(self, data):
        url = self.path('applicants/enable')
        return requests.post(url, data=data)

    def registry(self, token):
        url = self.path('applicants/{}'.format(token))
        return requests.get(url)

    def approve(self, token, email_address):
        data = {'email_address': email_address}
        url = self.path('applicants/{}/approve'.format(token))
        return requests.post(url, data=data)

    def path(self, endpoint):
        return '{}/api/{}/{}'.format(env.api_url, self.version, endpoint)

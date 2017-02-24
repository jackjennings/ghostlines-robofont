import requests

import mojo.roboFont as RF
from mojo.extensions import ExtensionBundle

from ghostlines import env


class Ghostlines(object):

    def __init__(self, version, token=None):
        self.version = version
        self.token = token

    def send(self, otf=None, recipients=None, notes=None, designer_email_address=None, license=None):
        if not otf and not recipients:
            return

        url = self.path('send')

        files = {
            'otf': otf
        }

        data = {
            'recipients': recipients,
            'notes': notes,
            'designer_email_address': designer_email_address
        }

        if license is not None:
            files['license'] = license

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

    # V1

    def create_font_family(self, name, designer):
        data = {'name': name, 'designer_name': designer}
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('font_family')
        return self.post(url, data=data, headers=headers)

    def font_family(self, id):
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('font_family/{}'.format(id))
        return self.get(url, headers=headers)

    def create_subscriber(self, font_family_id, name, email_address):
        data = {'font_family_id': font_family_id, 'name': name, 'email_address': email_address}
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('subscriber')
        return self.post(url, data=data, headers=headers)

    def delete_subscriber(self, id):
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('subscriber/{}'.format(id))
        return self.delete(url, headers=headers)

    def enable_applicants_v1(self, font_family_id):
        data = {'font_family_id': font_family_id}
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('applicant/enable')
        return self.post(url, data=data, headers=headers)

    def applicant_roster(self, id):
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('applicant/{}'.format(id))
        return self.get(url, headers=headers)

    def approve_applicant(self, id):
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('applicant/{}/approve'.format(id))
        return self.post(url, headers=headers)

    def create_release(self, otfs=[], license=None, **data):
        files = [('otfs[]', o) for o in otfs]

        if license:
            files.append(('license', license))

        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('release')
        return self.post(url, data=data, headers=headers, files=files)

    def authenticate(self, email_address, password):
        data = {'email_address': email_address, 'password': password}
        url = self.path('authenticate')
        return self.post(url, data=data)

    def account(self):
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('account')
        return self.get(url, headers=headers)

    def migrate(self, subscriber_email_addresses, font_family_name, designer_name, applicant_roster_token):
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        data = {
            'subscriber_email_addresses': subscriber_email_addresses,
            'font_family_name': font_family_name,
            'designer_name': designer_name,
            'applicant_roster_token': applicant_roster_token
        }
        url = self.path('migrate')
        return self.post(url, json=data, headers=headers)

    # Utilities

    def get(self, url, headers=None, **kwargs):
        if headers is None:
            headers = {}

        self.inject_version_data(headers)
        return requests.get(url, headers=headers, **kwargs)

    def post(self, url, headers=None, **kwargs):
        if headers is None:
            headers = {}

        self.inject_version_data(headers)
        return requests.post(url, headers=headers, **kwargs)

    def delete(self, url, headers=None, **kwargs):
        if headers is None:
            headers = {}

        self.inject_version_data(headers)
        return requests.delete(url, headers=headers, **kwargs)

    def inject_version_data(self, headers):
        extension = ExtensionBundle("Ghostlines").version or "Beta"
        version = "RF{};{}".format(RF.version, extension)
        headers["X-Ghostlines-Version"] = version

    def path(self, endpoint):
        return '{}/{}/{}'.format(env.api_url, self.version, endpoint)

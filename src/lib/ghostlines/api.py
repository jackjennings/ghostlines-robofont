import requests

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
        return requests.post(url, data=data, headers=headers)

    def font_family(self, id):
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('font_family/{}'.format(id))
        return requests.get(url, headers=headers)

    def create_subscriber(self, font_family_id, name, email_address):
        data = {'font_family_id': font_family_id, 'name': name, 'email_address': email_address}
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('subscriber')
        return requests.post(url, data=data, headers=headers)

    def delete_subscriber(self, id):
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('subscriber/{}'.format(id))
        return requests.delete(url, headers=headers)

    def enable_applicants_v1(self, font_family_id):
        data = {'font_family_id': font_family_id}
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('applicant/enable')
        return requests.post(url, data=data, headers=headers)

    def applicant_roster(self, id):
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('applicant/{}'.format(id))
        return requests.get(url, headers=headers)

    def approve_applicant(self, id):
        headers = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.path('applicant/{}/approve'.format(id))
        return requests.post(url, headers=headers)

    def path(self, endpoint):
        return '{}/{}/{}'.format(env.api_url, self.version, endpoint)

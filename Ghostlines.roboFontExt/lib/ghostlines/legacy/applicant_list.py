import webbrowser

from ghostlines.api import Ghostlines
from ghostlines.dashed_rectangle import DashedRectangle

from vanilla import Group, Button, List, TextBox


def CenteredButton(boxWidth, boxHeight, width, height, *args, **kwargs):
    return Button(((boxWidth / 2 - width / 2), (boxHeight / 2 - height / 2), width, height),
                  *args,
                  **kwargs)


class ApplicantList(Group):

    def __init__(self, dimensions, font, applicants, recipients, after_approve=None):
        super(ApplicantList, self).__init__(dimensions)

        _, _, width, height = self.getPosSize()

        self.recipients = recipients
        self.applicants = applicants
        self.font = font
        self.after_approve = after_approve

        self.border = DashedRectangle((0, 0, width, height))
        self.activate_registry_button = CenteredButton(width, height, 190, 24,
                                                       "Create Application Form",
                                                       callback=self.activate)

        self.label = TextBox((0, 0, -0, 22), "Applicants")
        self.list = List((0, 23, 0, -34), applicants)
        self.approve_applicant_button = Button((0, -24, 90, 24),
                                               "Approve",
                                               callback=self.approve_applicant)
        self.open_registration_page_button = Button((-150, -20, 150, 17),
                                                    "Open Application Form",
                                                    callback=self.open_registration_page,
                                                    sizeStyle="small")

        self.activated = font.lib.has_key('pm.ghostlines.ghostlines.registry_token')

    def open_registration_page(self, *args):
        response = Ghostlines('v0.1').registry(self.font.lib['pm.ghostlines.ghostlines.registry_token'])
        registry = response.json()
        webbrowser.open(registry['url'])

    def approve_applicant(self, *args):
        selected_applicants = [self.list[i] for i in self.list.getSelection()]

        for applicant in selected_applicants:
            Ghostlines('v0.1').approve(self.font.lib['pm.ghostlines.ghostlines.registry_token'], applicant)
            self.after_approve(applicant)

        self.fetch()

    def activate(self, *args):
        response = Ghostlines('v0.1').enable_applicants({
            'font_name': self.font.info.familyName,
            'designer': self.font.info.designer
        })

        registry = response.json()

        self.font.lib['pm.ghostlines.ghostlines.registry_token'] = registry['token']
        self.activated = True

    def fetch(self):
        if self.font.lib.has_key('pm.ghostlines.ghostlines.registry_token'):
            response = Ghostlines('v0.1').registry(self.font.lib['pm.ghostlines.ghostlines.registry_token'])
            registry = response.json()
            applicant_emails = [r['email_address'] for r in registry['applicants'] if not r['approved_at']]

            self.list.set(applicant_emails)

    @property
    def activated(self):
        return self._activated

    @activated.setter
    def activated(self, value):
        self._activated = value

        self.label.show(value)
        self.list.show(value)
        self.approve_applicant_button.show(value)
        self.border.show(not value)
        self.activate_registry_button.show(not value)
        self.open_registration_page_button.show(value)

        return self.activated

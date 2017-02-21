import webbrowser

from ghostlines.api import Ghostlines
from ghostlines.dashed_rectangle import DashedRectangle
from ghostlines.error_message import ErrorMessage
from ghostlines.storage.app_storage import AppStorage

from vanilla import Group, Button, List, TextBox


def CenteredButton(boxWidth, boxHeight, width, height, *args, **kwargs):
    return Button(((boxWidth / 2 - width / 2), (boxHeight / 2 - height / 2), width, height),
                  *args,
                  **kwargs)


class ApplicantList(Group):

    columns = [
        {
            "title": "Name",
            "key": "name",
            "editable": False
        }, {
            "title": "Email Address",
            "key": "email_address",
            "editable": False
        }
    ]

    def __init__(self, dimensions, applicant_roster, font_family_id, after_approve=None):
        super(ApplicantList, self).__init__(dimensions)

        _, _, width, height = self.getPosSize()

        self.applicant_roster = applicant_roster
        self.family_id = font_family_id
        self.after_approve = after_approve

        self.border = DashedRectangle((0, 0, width, height))
        self.enable_registry_button = CenteredButton(width, height, 190, 24,
                                                     "Create Application Form",
                                                     callback=self.enable)

        self.label = TextBox((0, 0, -0, 22), "Applicants")
        # TODO: Add applicants
        self.list = List((0, 23, 0, -34), [], columnDescriptions=self.columns)
        self.approve_applicant_button = Button((0, -24, 90, 24),
                                               "Approve",
                                               callback=self.approve_applicant)
        self.open_registration_page_button = Button((-150, -20, 150, 17),
                                                    "Open Application Form",
                                                    callback=self.open_registration_page,
                                                    sizeStyle="small")

        self.enabled = self.applicant_roster is not None

    def open_registration_page(self, *args):
        webbrowser.open(self.applicant_roster['url'])

    def approve_applicant(self, *args):
        selected_applicants = [self.list[i] for i in self.list.getSelection()]

        for applicant in selected_applicants:
            token = AppStorage("pm.ghostlines.ghostlines.access_token").retrieve()
            Ghostlines('v1', token=token).approve_applicant(applicant["id"])

        self.after_approve()
        self.fetch()

    def enable(self, *args):
        token = AppStorage("pm.ghostlines.ghostlines.access_token").retrieve()
        response = Ghostlines('v1', token=token).enable_applicants_v1(self.family_id)
        json = response.json()

        if response.status_code == 201:
            self.applicant_roster = json
            self.enabled = True
        else:
            ErrorMessage("Could not enable applicants", json["errors"]).open()

    def fetch(self):
        if self.enabled:
            token = AppStorage("pm.ghostlines.ghostlines.access_token").retrieve()
            response = Ghostlines('v1', token=token).applicant_roster(self.family_id)
            self.applicant_roster = response.json()
            self.set(self.applicant_roster["applicants"])

    def set(self, applicants):
        unapproved = [a for a in applicants if a["approved_at"] is None]
        self.list.set(unapproved)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

        self.label.show(value)
        self.list.show(value)
        self.approve_applicant_button.show(value)
        self.border.show(not value)
        self.enable_registry_button.show(not value)
        self.open_registration_page_button.show(value)

        return self.enabled

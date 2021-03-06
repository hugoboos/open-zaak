from django.urls import reverse

import requests_mock
from django_webtest import WebTest

from openzaak.accounts.tests.factories import SuperUserFactory
from openzaak.selectielijst.tests import (
    mock_oas_get,
    mock_resource_get,
    mock_resource_list,
)
from openzaak.utils.tests import ClearCachesMixin

from ..factories import ResultaatTypeFactory


@requests_mock.Mocker()
class ResultaattypeAdminTests(ClearCachesMixin, WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        super().setUp()

        self.app.set_user(self.user)

    def test_zaaktypen_list(self, m):
        ResultaatTypeFactory.create()
        url = reverse("admin:catalogi_resultaattype_changelist")

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)

    def test_resultaattype_detail(self, m):
        procestype_url = (
            "https://referentielijsten-api.vng.cloud/api/v1/"
            "procestypen/e1b73b12-b2f6-4c4e-8929-94f84dd2a57d"
        )
        mock_oas_get(m)
        mock_resource_list(m, "resultaattypeomschrijvingen")
        mock_resource_list(m, "resultaten")
        mock_resource_get(m, "procestypen", procestype_url)
        resultaattype = ResultaatTypeFactory.create(
            zaaktype__selectielijst_procestype=procestype_url
        )
        url = reverse("admin:catalogi_resultaattype_change", args=(resultaattype.pk,))

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)

    def test_selectielijst_selectielijstklasse(self, m):
        """
        Test that the selectielijst procestype field is a dropdown.
        """
        procestype_url = (
            "https://referentielijsten-api.vng.cloud/api/v1/"
            "procestypen/e1b73b12-b2f6-4c4e-8929-94f84dd2a57d"
        )
        mock_oas_get(m)
        mock_resource_list(m, "resultaattypeomschrijvingen")
        mock_resource_list(m, "resultaten")
        mock_resource_get(m, "procestypen", procestype_url)
        zaaktype = ResultaatTypeFactory.create(
            zaaktype__selectielijst_procestype=procestype_url
        )
        url = reverse("admin:catalogi_resultaattype_change", args=(zaaktype.pk,))

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)

        form = response.forms["resultaattype_form"]
        field = form.fields["selectielijstklasse"][0]
        self.assertEqual(field.tag, "input")
        # first element of JSON response
        self.assertEqual(
            field._value,
            "https://referentielijsten-api.vng.cloud/api/v1/resultaten/cc5ae4e3-a9e6-4386-bcee-46be4986a829",
        )

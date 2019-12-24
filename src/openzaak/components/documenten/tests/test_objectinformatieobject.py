from django.test import override_settings, tag

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import ObjectTypes
from vng_api_common.tests import (
    JWTAuthMixin,
    get_validation_errors,
    reverse,
    reverse_lazy,
)

from openzaak.components.besluiten.tests.factories import (
    BesluitFactory,
    BesluitInformatieObjectFactory,
)
from openzaak.components.besluiten.tests.utils import get_besluit_response
from openzaak.components.zaken.tests.factories import (
    ZaakFactory,
    ZaakInformatieObjectFactory,
)
from openzaak.components.zaken.tests.utils import get_zaak_response

from ..models import ObjectInformatieObject
from .factories import EnkelvoudigInformatieObjectFactory


@tag("oio")
class ObjectInformatieObjectTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True
    list_url = reverse_lazy("objectinformatieobject-list")

    def test_create_with_objecttype_zaak(self):
        zaak = ZaakFactory.create()
        eio = EnkelvoudigInformatieObjectFactory.create()
        # relate the two
        ZaakInformatieObjectFactory.create(zaak=zaak, informatieobject=eio.canonical)

        # get OIO created via signals
        oio = ObjectInformatieObject.objects.get()

        zaak_url = reverse(zaak)
        eio_url = reverse(eio)

        response = self.client.post(
            self.list_url,
            {
                "object": f"http://testserver{zaak_url}",
                "informatieobject": f"http://testserver{eio_url}",
                "objectType": "zaak",
            },
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "unique")

    def test_create_with_objecttype_besluit(self):
        besluit = BesluitFactory.create()
        eio = EnkelvoudigInformatieObjectFactory.create()
        # relate the two
        BesluitInformatieObjectFactory.create(
            besluit=besluit, informatieobject=eio.canonical
        )

        # get OIO created via signals
        oio = ObjectInformatieObject.objects.get()

        besluit_url = reverse(besluit)
        eio_url = reverse(eio)
        oio_url = reverse("objectinformatieobject-detail", kwargs={"uuid": oio.uuid})

        response = self.client.post(
            self.list_url,
            {
                "object": f"http://testserver{besluit_url}",
                "informatieobject": f"http://testserver{eio_url}",
                "objectType": "besluit",
            },
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "unique")

    def test_create_with_objecttype_other_fail(self):
        besluit = BesluitFactory.create()
        eio = EnkelvoudigInformatieObjectFactory.create()
        # relate the two
        BesluitInformatieObjectFactory.create(
            besluit=besluit, informatieobject=eio.canonical
        )

        besluit_url = reverse(besluit)
        eio_url = reverse(eio)

        response = self.client.post(
            self.list_url,
            {
                "object": f"http://testserver{besluit_url}",
                "informatieobject": f"http://testserver{eio_url}",
                "objectType": "other",
            },
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )
        error = get_validation_errors(response, "objectType")
        self.assertEqual(error["code"], "invalid_choice")

    def test_read_with_objecttype_zaak(self):
        zaak = ZaakFactory.create()
        eio = EnkelvoudigInformatieObjectFactory.create()
        # relate the two
        ZaakInformatieObjectFactory.create(zaak=zaak, informatieobject=eio.canonical)

        # get OIO created via signals
        oio = ObjectInformatieObject.objects.get()

        oio_url = reverse("objectinformatieobject-detail", kwargs={"uuid": oio.uuid})
        zaak_url = reverse(zaak)
        eio_url = reverse(eio)

        response = self.client.get(oio_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(
            response.data,
            {
                "url": f"http://testserver{oio_url}",
                "object": f"http://testserver{zaak_url}",
                "informatieobject": f"http://testserver{eio_url}",
                "object_type": "zaak",
            },
        )

    def test_read_with_objecttype_besluit(self):
        besluit = BesluitFactory.create()
        eio = EnkelvoudigInformatieObjectFactory.create()
        # relate the two
        BesluitInformatieObjectFactory.create(
            besluit=besluit, informatieobject=eio.canonical
        )

        # get OIO created via signals
        oio = ObjectInformatieObject.objects.get()

        oio_url = reverse("objectinformatieobject-detail", kwargs={"uuid": oio.uuid})
        besluit_url = reverse(besluit)
        eio_url = reverse(eio)

        response = self.client.get(oio_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(
            response.data,
            {
                "url": f"http://testserver{oio_url}",
                "object": f"http://testserver{besluit_url}",
                "informatieobject": f"http://testserver{eio_url}",
                "object_type": "besluit",
            },
        )

    def test_post_object_without_created_relations(self):
        """
        Test the (informatieobject, object) unique together validation.

        This is expected to fail, since there is no actual creation in database.
        It will however become relevant again when we're handling remote
        references.
        """
        zaak = ZaakFactory.create()
        eio = EnkelvoudigInformatieObjectFactory.create()
        zaak_url = reverse(zaak)
        eio_url = reverse(eio)

        content = {
            "informatieobject": f"http://testserver{eio_url}",
            "object": f"http://testserver{zaak_url}",
            "objectType": ObjectTypes.zaak,
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "inconsistent-relation")

    def test_filter_eio(self):
        bio = BesluitInformatieObjectFactory.create()
        ZaakInformatieObjectFactory.create()  # may not show up
        eio_detail_url = reverse(bio.informatieobject.latest_version)

        response = self.client.get(
            self.list_url,
            {"informatieobject": f"http://openzaak.nl{eio_detail_url}"},
            HTTP_HOST="openzaak.nl",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["informatieobject"], f"http://openzaak.nl{eio_detail_url}"
        )

    def test_filter_zaak(self):
        zio = ZaakInformatieObjectFactory.create()
        ZaakInformatieObjectFactory.create()  # may not show up
        eio_detail_url = reverse(zio.informatieobject.latest_version)
        zaak_url = reverse(zio.zaak)

        response = self.client.get(
            self.list_url,
            {"object": f"http://openzaak.nl{zaak_url}"},
            HTTP_HOST="openzaak.nl",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["informatieobject"], f"http://openzaak.nl{eio_detail_url}"
        )

    def test_filter_besluit(self):
        bio = BesluitInformatieObjectFactory.create()
        BesluitInformatieObjectFactory.create()  # may not show up
        bio_detail_url = reverse(bio.informatieobject.latest_version)
        besluit_url = reverse(bio.besluit)

        response = self.client.get(
            self.list_url,
            {"object": f"http://openzaak.nl{besluit_url}"},
            HTTP_HOST="openzaak.nl",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["informatieobject"], f"http://openzaak.nl{bio_detail_url}"
        )

    def test_validate_unknown_query_params(self):
        url = reverse(ObjectInformatieObject)

        response = self.client.get(url, {"someparam": "somevalue"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "unknown-parameters")


class ObjectInformatieObjectDestroyTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_destroy_oio_remote_gone(self):
        zio = ZaakInformatieObjectFactory.create()
        oio = ObjectInformatieObject.objects.get()
        url = reverse(oio)
        zio.delete()

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_oio_remote_still_present(self):
        BesluitInformatieObjectFactory.create()
        oio = ObjectInformatieObject.objects.get()
        url = reverse(oio)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "inconsistent-relation")


@tag("external-urls")
@override_settings(ALLOWED_HOSTS=["testserver"])
class ResultaatCreateExternalURLsTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True
    list_url = reverse(ObjectInformatieObject)

    def test_create_external_zaak(self):
        zaak = "https://externe.catalogus.nl/api/v1/zaken/1c8e36be-338c-4c07-ac5e-1adf55bec04a"
        zaaktype = "https://externe.catalogus.nl/api/v1/zaaktypen/b71f72ef-198d-44d8-af64-ae1932df830a"

        eio = EnkelvoudigInformatieObjectFactory.create()
        eio_url = reverse(eio)

        with requests_mock.Mocker(real_http=True) as m:
            m.get(zaak, json=get_zaak_response(zaak, zaaktype))

            response = self.client.post(
                self.list_url,
                {
                    "object": zaak,
                    "informatieobject": f"http://testserver{eio_url}",
                    "objectType": "zaak",
                },
            )

            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, response.data
            )

            oio = ObjectInformatieObject.objects.get()

            self.assertEqual(oio.informatieobject, eio.canonical)
            self.assertEqual(oio.object, zaak)

    def test_create_external_besluit(self):
        besluit = "https://externe.catalogus.nl/api/v1/besluiten/1c8e36be-338c-4c07-ac5e-1adf55bec04a"
        besluittype = "https://externe.catalogus.nl/api/v1/besluittypen/b71f72ef-198d-44d8-af64-ae1932df830a"

        eio = EnkelvoudigInformatieObjectFactory.create()
        eio_url = reverse(eio)

        with requests_mock.Mocker(real_http=True) as m:
            m.get(besluit, json=get_besluit_response(besluit, besluittype))

            response = self.client.post(
                self.list_url,
                {
                    "object": besluit,
                    "informatieobject": f"http://testserver{eio_url}",
                    "objectType": "besluit",
                },
            )

            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, response.data
            )

            oio = ObjectInformatieObject.objects.get()

            self.assertEqual(oio.informatieobject, eio.canonical)
            self.assertEqual(oio.object, besluit)

    def test_create_external_zaak_fail_invalid_schema(self):
        zaak = "https://externe.catalogus.nl/api/v1/zaken/1c8e36be-338c-4c07-ac5e-1adf55bec04a"
        zaaktype = "https://externe.catalogus.nl/api/v1/zaaktypen/b71f72ef-198d-44d8-af64-ae1932df830a"

        eio = EnkelvoudigInformatieObjectFactory.create()
        eio_url = reverse(eio)

        with requests_mock.Mocker(real_http=True) as m:
            m.get(
                zaak,
                json={
                    "url": zaak,
                    "uuid": "d781cd1b-f100-4051-9543-153b93299da4",
                    "identificatie": "ZAAK-2019-0000000001",
                    "zaaktype": zaaktype,
                },
            )

            response = self.client.post(
                self.list_url,
                {
                    "object": zaak,
                    "informatieobject": f"http://testserver{eio_url}",
                    "objectType": "zaak",
                },
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "object")
        self.assertEqual(error["code"], "invalid-resource")

    def test_create_external_besluit_fail_invalid_schema(self):
        besluit = "https://externe.catalogus.nl/api/v1/besluiten/1c8e36be-338c-4c07-ac5e-1adf55bec04a"
        besluittype = "https://externe.catalogus.nl/api/v1/besluittypen/b71f72ef-198d-44d8-af64-ae1932df830a"

        eio = EnkelvoudigInformatieObjectFactory.create()
        eio_url = reverse(eio)

        with requests_mock.Mocker(real_http=True) as m:
            m.get(
                besluit,
                json={
                    "url": besluit,
                    "identificatie": "BESLUIT-2019-0000000001",
                    "besluittype": besluittype,
                },
            )

            response = self.client.post(
                self.list_url,
                {
                    "object": besluit,
                    "informatieobject": f"http://testserver{eio_url}",
                    "objectType": "besluit",
                },
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "object")
        self.assertEqual(error["code"], "invalid-resource")

    def test_create_fail_not_unique(self):
        besluit = "https://externe.catalogus.nl/api/v1/besluiten/1c8e36be-338c-4c07-ac5e-1adf55bec04a"
        besluittype = "https://externe.catalogus.nl/api/v1/besluittypen/b71f72ef-198d-44d8-af64-ae1932df830a"
        eio = EnkelvoudigInformatieObjectFactory.create()
        eio_url = reverse(eio)

        ObjectInformatieObject.objects.create(
            informatieobject=eio.canonical, besluit=besluit, object_type="besluit"
        )

        with requests_mock.Mocker(real_http=True) as m:
            m.get(besluit, json=get_besluit_response(besluit, besluittype))

            response = self.client.post(
                self.list_url,
                {
                    "object": besluit,
                    "informatieobject": f"http://testserver{eio_url}",
                    "objectType": "besluit",
                },
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "unique")

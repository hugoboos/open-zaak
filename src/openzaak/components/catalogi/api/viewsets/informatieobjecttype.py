from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from vng_api_common.viewsets import CheckQueryParamsMixin

from openzaak.utils.permissions import AuthRequired

from ...models import InformatieObjectType
from ..filters import InformatieObjectTypeFilter
from ..scopes import (
    SCOPE_ZAAKTYPES_FORCED_DELETE,
    SCOPE_ZAAKTYPES_READ,
    SCOPE_ZAAKTYPES_WRITE,
)
from ..serializers import InformatieObjectTypeSerializer
from .mixins import ConceptMixin, M2MConceptDestroyMixin


class InformatieObjectTypeViewSet(
    CheckQueryParamsMixin, ConceptMixin, M2MConceptDestroyMixin, viewsets.ModelViewSet
):
    """
    Opvragen en bewerken van INFORMATIEOBJECTTYPEn nodig voor
    INFORMATIEOBJECTen in de Documenten API.

    Een INFORMATIEOBJECTTYPE beschijft de karakteristieken van een document of
    ander object dat informatie bevat.

    create:
    Maak een INFORMATIEOBJECTTYPE aan.

    Maak een INFORMATIEOBJECTTYPE aan.

    list:
    Alle INFORMATIEOBJECTTYPEn opvragen.

    Deze lijst kan gefilterd wordt met query-string parameters.

    retrieve:
    Een specifieke INFORMATIEOBJECTTYPE opvragen.

    Een specifieke INFORMATIEOBJECTTYPE opvragen.

    update:
    Werk een INFORMATIEOBJECTTYPE in zijn geheel bij.

    Werk een INFORMATIEOBJECTTYPE in zijn geheel bij. Dit kan alleen als het een
    concept betreft.

    partial_update:
    Werk een INFORMATIEOBJECTTYPE deels bij.

    Werk een INFORMATIEOBJECTTYPE deels bij. Dit kan alleen als het een concept
    betreft.

    destroy:
    Verwijder een INFORMATIEOBJECTTYPE.

    Verwijder een INFORMATIEOBJECTTYPE. Dit kan alleen als het een concept
    betreft.
    """

    queryset = InformatieObjectType.objects.all().order_by("-pk")
    serializer_class = InformatieObjectTypeSerializer
    filterset_class = InformatieObjectTypeFilter
    lookup_field = "uuid"
    pagination_class = PageNumberPagination
    permission_classes = (AuthRequired,)
    required_scopes = {
        "list": SCOPE_ZAAKTYPES_READ,
        "retrieve": SCOPE_ZAAKTYPES_READ,
        "create": SCOPE_ZAAKTYPES_WRITE,
        "update": SCOPE_ZAAKTYPES_WRITE,
        "partial_update": SCOPE_ZAAKTYPES_WRITE,
        "destroy": SCOPE_ZAAKTYPES_WRITE | SCOPE_ZAAKTYPES_FORCED_DELETE,
        "publish": SCOPE_ZAAKTYPES_WRITE,
    }
    concept_related_fields = ["besluittypen", "zaaktypes"]
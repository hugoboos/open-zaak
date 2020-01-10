from django.contrib import admin

from openzaak.utils.admin import (
    AuditTrailAdminMixin,
    EditInlineAdminMixin,
    UUIDAdminMixin,
)

from ..models import (
    KlantContact,
    RelevanteZaakRelatie,
    Resultaat,
    Rol,
    Status,
    Zaak,
    ZaakBesluit,
    ZaakEigenschap,
    ZaakInformatieObject,
    ZaakObject,
)
from .betrokkenen import (
    MedewerkerInline,
    NatuurlijkPersoonInline,
    NietNatuurlijkPersoonInline,
    OrganisatorischeEenheidInline,
    VestigingInline,
)
from .objecten import (
    AdresInline,
    BuurtInline,
    GemeenteInline,
    GemeentelijkeOpenbareRuimteInline,
    HuishoudenInline,
    InrichtingselementInline,
    KadastraleOnroerendeZaakInline,
    KunstwerkdeelInline,
    MaatschappelijkeActiviteitInline,
    OpenbareRuimteInline,
    OverigeInline,
    PandInline,
    SpoorbaandeelInline,
    TerreindeelInline,
    TerreinGebouwdObjectInline,
    WaterdeelInline,
    WegdeelInline,
    WijkInline,
    WoonplaatsInline,
    WozDeelobjectInline,
    WozObjectInline,
    WozWaardeInline,
    ZakelijkRechtInline,
)


@admin.register(Status)
class StatusAdmin(AuditTrailAdminMixin, UUIDAdminMixin, admin.ModelAdmin):
    list_display = ("zaak", "datum_status_gezet")
    list_select_related = ("zaak",)
    list_filter = ("datum_status_gezet",)
    search_fields = (
        "uuid",
        "statustoelichting",
    )
    ordering = ("datum_status_gezet",)
    raw_id_fields = ("zaak", "_statustype")
    viewset = "openzaak.components.zaken.api.viewsets.StatusViewSet"


@admin.register(ZaakObject)
class ZaakObjectAdmin(AuditTrailAdminMixin, UUIDAdminMixin, admin.ModelAdmin):
    list_display = ("zaak", "object_type", "object", "relatieomschrijving")
    list_select_related = ("zaak",)
    list_filter = ("object_type",)
    search_fields = ("uuid", "object", "relatieomschrijving")
    ordering = ("object_type", "object")
    raw_id_fields = ("zaak",)
    viewset = "openzaak.components.zaken.api.viewsets.ZaakObjectViewSet"
    inlines = [
        AdresInline,
        BuurtInline,
        GemeenteInline,
        GemeentelijkeOpenbareRuimteInline,
        HuishoudenInline,
        InrichtingselementInline,
        KadastraleOnroerendeZaakInline,
        KunstwerkdeelInline,
        MaatschappelijkeActiviteitInline,
        OpenbareRuimteInline,
        OverigeInline,
        PandInline,
        SpoorbaandeelInline,
        TerreindeelInline,
        TerreinGebouwdObjectInline,
        WaterdeelInline,
        WegdeelInline,
        WijkInline,
        WoonplaatsInline,
        WozDeelobjectInline,
        WozObjectInline,
        WozWaardeInline,
        ZakelijkRechtInline,
        NatuurlijkPersoonInline,
        NietNatuurlijkPersoonInline,
        OrganisatorischeEenheidInline,
        VestigingInline,
        MedewerkerInline,
    ]


@admin.register(KlantContact)
class KlantContactAdmin(AuditTrailAdminMixin, UUIDAdminMixin, admin.ModelAdmin):
    list_display = ("zaak", "identificatie", "datumtijd", "kanaal")
    list_select_related = ("zaak",)
    list_filter = ("datumtijd",)
    search_fields = ("uuid", "identificatie", "toelichting", "kanaal")
    ordering = ("identificatie", "datumtijd")
    raw_id_fields = ("zaak",)
    viewset = "openzaak.components.zaken.api.viewsets.KlantContactViewSet"


@admin.register(ZaakEigenschap)
class ZaakEigenschapAdmin(AuditTrailAdminMixin, UUIDAdminMixin, admin.ModelAdmin):
    list_display = ("zaak", "_eigenschap", "_eigenschap_url", "waarde")
    list_select_related = ("zaak",)
    list_filter = ("_naam",)
    search_fields = ("uuid", "_naam", "waarde")
    ordering = ("zaak", "_eigenschap", "_eigenschap_url")
    raw_id_fields = ("zaak", "_eigenschap")
    viewset = "openzaak.components.zaken.api.viewsets.ZaakEigenschapViewSet"


@admin.register(ZaakInformatieObject)
class ZaakInformatieObjectAdmin(AuditTrailAdminMixin, UUIDAdminMixin, admin.ModelAdmin):
    list_display = ("zaak", "_informatieobject", "_informatieobject_url")
    list_select_related = ("zaak", "_informatieobject")
    list_filter = ("aard_relatie",)
    search_fields = ("uuid", "zaak", "_informatieobject", "_informatieobject_url")
    ordering = ("zaak", "_informatieobject", "_informatieobject_url")
    raw_id_fields = ("zaak", "_informatieobject")
    viewset = "openzaak.components.zaken.api.viewsets.ZaakInformatieObjectViewSet"


@admin.register(Resultaat)
class ResultaatAdmin(AuditTrailAdminMixin, UUIDAdminMixin, admin.ModelAdmin):
    list_display = ("zaak", "toelichting")
    list_select_related = ("zaak", "_resultaattype")
    search_fields = ("uuid", "toelichting", "_resultaattype", "_resultaattype_url")
    ordering = ("zaak",)
    raw_id_fields = ("zaak", "_resultaattype")
    viewset = "openzaak.components.zaken.api.viewsets.ResultaatViewSet"


@admin.register(Rol)
class RolAdmin(AuditTrailAdminMixin, UUIDAdminMixin, admin.ModelAdmin):
    list_display = ("zaak", "betrokkene", "betrokkene_type")
    list_select_related = ("zaak",)
    list_filter = ("betrokkene_type", "indicatie_machtiging", "registratiedatum")
    search_fields = (
        "uuid",
        "betrokkene",
        "omschrijving",
        "roltoelichting",
    )
    ordering = ("registratiedatum", "betrokkene")
    raw_id_fields = ("zaak", "_roltype")
    viewset = "openzaak.components.zaken.api.viewsets.RolViewSet"
    inlines = [
        NatuurlijkPersoonInline,
        NietNatuurlijkPersoonInline,
        OrganisatorischeEenheidInline,
        VestigingInline,
        MedewerkerInline,
    ]


@admin.register(RelevanteZaakRelatie)
class RelevanteZaakRelatieAdmin(admin.ModelAdmin):
    list_display = ("zaak", "_relevant_zaak", "_relevant_zaak_url")
    list_filter = ("aard_relatie",)
    search_fields = ("zaak", "_relevant_zaak", "_relevant_zaak_url")
    ordering = ("zaak", "_relevant_zaak", "_relevant_zaak_url")
    raw_id_fields = ("zaak", "_relevant_zaak")
    list_select_related = ("zaak",)


@admin.register(ZaakBesluit)
class ZaakBesluitAdmin(AuditTrailAdminMixin, UUIDAdminMixin, admin.ModelAdmin):
    list_display = ("zaak", "_besluit", "_besluit_url")
    list_select_related = ("zaak",)
    search_fields = ("uuid", "zaak", "_besluit", "_besluit_url")
    ordering = ("zaak", "_besluit", "_besluit_url")
    raw_id_fields = ("zaak", "_besluit")
    viewset = "openzaak.components.zaken.api.viewsets.ZaakBesluitViewSet"


# inline classes for Zaak
class StatusInline(EditInlineAdminMixin, admin.TabularInline):
    model = Status
    fields = StatusAdmin.list_display


class ZaakObjectInline(EditInlineAdminMixin, admin.TabularInline):
    model = ZaakObject
    fields = ZaakObjectAdmin.list_display


class ZaakEigenschapInline(EditInlineAdminMixin, admin.TabularInline):
    model = ZaakEigenschap
    fields = ZaakEigenschapAdmin.list_display


class ZaakInformatieObjectInline(EditInlineAdminMixin, admin.TabularInline):
    model = ZaakInformatieObject
    fields = ZaakInformatieObjectAdmin.list_display


class KlantContactInline(EditInlineAdminMixin, admin.TabularInline):
    model = KlantContact
    fields = KlantContactAdmin.list_display


class RolInline(EditInlineAdminMixin, admin.TabularInline):
    model = Rol
    fields = RolAdmin.list_display


class ResultaatInline(EditInlineAdminMixin, admin.TabularInline):
    model = Resultaat
    fields = ResultaatAdmin.list_display


class RelevanteZaakRelatieInline(EditInlineAdminMixin, admin.TabularInline):
    model = RelevanteZaakRelatie
    fk_name = "zaak"
    fields = RelevanteZaakRelatieAdmin.list_display


class ZaakBesluitInline(EditInlineAdminMixin, admin.TabularInline):
    model = ZaakBesluit
    fields = ZaakBesluitAdmin.list_display


@admin.register(Zaak)
class ZaakAdmin(AuditTrailAdminMixin, UUIDAdminMixin, admin.ModelAdmin):
    list_display = (
        "identificatie",
        "registratiedatum",
        "startdatum",
        "einddatum",
        "archiefstatus",
    )
    search_fields = (
        "identificatie",
        "uuid",
    )
    date_hierarchy = "registratiedatum"
    list_filter = ("startdatum", "archiefstatus", "vertrouwelijkheidaanduiding")
    ordering = ("identificatie", "startdatum")
    inlines = [
        StatusInline,
        ZaakObjectInline,
        ZaakInformatieObjectInline,
        KlantContactInline,
        ZaakEigenschapInline,
        RolInline,
        ResultaatInline,
        RelevanteZaakRelatieInline,
    ]
    raw_id_fields = ("_zaaktype", "hoofdzaak")
    viewset = "openzaak.components.zaken.api.viewsets.ZaakViewSet"


@admin.register(Status)
class StatusAdmin(AuditTrailAdminMixin, admin.ModelAdmin):
    list_display = ["zaak", "datum_status_gezet"]
    list_select_related = ["zaak"]
    raw_id_fields = ["zaak"]
    viewset = "openzaak.components.zaken.api.viewsets.StatusViewSet"
    readonly_fields = ("uuid",)


@admin.register(ZaakObject)
class ZaakObjectAdmin(AuditTrailAdminMixin, admin.ModelAdmin):
    list_display = ["zaak", "object", "relatieomschrijving"]
    list_select_related = ["zaak"]
    raw_id_fields = ["zaak"]
    viewset = "openzaak.components.zaken.api.viewsets.ZaakObjectViewSet"
    readonly_fields = ("uuid",)


@admin.register(KlantContact)
class KlantContactAdmin(AuditTrailAdminMixin, admin.ModelAdmin):
    list_display = ["zaak", "identificatie", "datumtijd", "kanaal"]
    list_select_related = ["zaak"]
    raw_id_fields = ["zaak"]
    viewset = "openzaak.components.zaken.api.viewsets.KlantContactViewSet"
    readonly_fields = ("uuid",)


@admin.register(ZaakEigenschap)
class ZaakEigenschapAdmin(AuditTrailAdminMixin, admin.ModelAdmin):
    list_display = ["zaak", "_eigenschap", "_eigenschap_url", "waarde"]
    list_select_related = ["zaak"]
    raw_id_fields = ["zaak"]
    viewset = "openzaak.components.zaken.api.viewsets.ZaakEigenschapViewSet"
    readonly_fields = ("uuid",)


@admin.register(ZaakInformatieObject)
class ZaakInformatieObjectAdmin(AuditTrailAdminMixin, admin.ModelAdmin):
    list_display = ["zaak", "_informatieobject", "_informatieobject_url"]
    list_select_related = ["zaak", "_informatieobject"]
    raw_id_fields = ["zaak", "_informatieobject"]
    viewset = "openzaak.components.zaken.api.viewsets.ZaakInformatieObjectViewSet"
    readonly_fields = ("uuid",)


@admin.register(Resultaat)
class ResultaatAdmin(AuditTrailAdminMixin, admin.ModelAdmin):
    list_display = ["zaak", "toelichting"]
    list_select_related = ["zaak"]
    raw_id_fields = ["zaak"]
    viewset = "openzaak.components.zaken.api.viewsets.ResultaatViewSet"
    readonly_fields = ("uuid",)


@admin.register(Rol)
class RolAdmin(AuditTrailAdminMixin, admin.ModelAdmin):
    list_display = ["zaak", "betrokkene", "betrokkene_type"]
    list_select_related = ["zaak"]
    raw_id_fields = ["zaak"]
    viewset = "openzaak.components.zaken.api.viewsets.RolViewSet"
    readonly_fields = ("uuid",)


@admin.register(ZaakBesluit)
class ZaakBesluitAdmin(admin.ModelAdmin):
    list_display = ["zaak", "_besluit", "_besluit_url"]
    list_select_related = ["zaak"]
    raw_id_fields = ["zaak"]
    readonly_fields = ("uuid",)

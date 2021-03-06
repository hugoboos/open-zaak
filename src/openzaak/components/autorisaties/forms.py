from typing import List, Tuple

from django import forms
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from vng_api_common.authorizations.models import Applicatie, Autorisatie
from vng_api_common.constants import ComponentTypes, VertrouwelijkheidsAanduiding
from vng_api_common.models import JWTSecret
from vng_api_common.notifications.constants import (
    SCOPE_NOTIFICATIES_CONSUMEREN_LABEL,
    SCOPE_NOTIFICATIES_PUBLICEREN_LABEL,
)
from vng_api_common.scopes import SCOPE_REGISTRY

from openzaak.components.catalogi.models import (
    BesluitType,
    InformatieObjectType,
    ZaakType,
)

from .constants import RelatedTypeSelectionMethods
from .utils import (
    get_applicatie_serializer,
    send_applicatie_changed_notification,
    versions_equivalent,
)


class ApplicatieForm(forms.ModelForm):
    class Meta:
        model = Applicatie
        # removed `client_ids arrayfield - replaced by and inline
        # doing stuff with JWTSecret
        fields = ("uuid", "label", "heeft_alle_autorisaties")

    def save(self, *args, **kwargs):
        if self.instance.client_ids is None:
            self.instance.client_ids = []
        return super().save(*args, **kwargs)


class CredentialsBaseFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance")
        queryset = kwargs.pop("queryset")
        kwargs.pop("save_as_new", None)

        if instance.client_ids:
            kwargs["queryset"] = queryset.filter(identifier__in=instance.client_ids)
        else:
            kwargs["queryset"] = queryset.none()

        self.instance = instance

        super().__init__(*args, **kwargs)

        # add default value for secret = ''
        self.form.base_fields["secret"].required = False
        self.form.base_fields["secret"].initial = ""

    @classmethod
    def get_default_prefix(cls):
        return "credentials"

    def save(self, *args, **kwargs):
        commit = kwargs.get("commit", True)
        creds = super().save(*args, **kwargs)

        old_identifiers = {
            form.instance.pk: form.initial["identifier"]
            for form in self.forms
            if form.instance.pk and "identifier" in form.initial
        }

        for cred in self.deleted_objects:
            self.instance.client_ids.remove(cred.identifier)

        for cred, changed in self.changed_objects:
            if "identifier" not in changed:
                continue

            old_identifier = old_identifiers[cred.id]
            self.instance.client_ids.remove(old_identifier)
            self.instance.client_ids.append(cred.identifier)

        for cred in creds:
            if cred.identifier in self.instance.client_ids:
                continue
            self.instance.client_ids.append(cred.identifier)

        if commit:
            self.instance.save(update_fields=["client_ids"])
        return creds


CredentialsFormSet = forms.modelformset_factory(
    JWTSecret,
    formset=CredentialsBaseFormSet,
    fields=("identifier", "secret"),
    extra=1,
    can_delete=True,
)


# Forms used for autorisaties in custom view - we use them for validation
# purposes, the actual rendering/dynamic behaviour is taken care off by
# React.

COMPONENT_TO_PREFIXES_MAP = {
    ComponentTypes.zrc: ("audittrails", "notificaties", "zaken"),
    ComponentTypes.drc: ("audittrails", "notificaties", "documenten"),
    ComponentTypes.ztc: ("notificaties", "catalogi"),
    ComponentTypes.brc: ("audittrails", "notificaties", "besluiten"),
    ComponentTypes.nrc: ("notificaties",),
    ComponentTypes.ac: ("notificaties", "autorisaties"),
}

COMPONENT_TO_FIELDS_MAP = {
    ComponentTypes.zrc: {
        "required": ("related_type_selection", "vertrouwelijkheidaanduiding"),
        "types_field": "zaaktypen",
        "_autorisatie_type_field": "zaaktype",
        "verbose_name": _("zaaktype"),
    },
    ComponentTypes.drc: {
        "required": ("related_type_selection", "vertrouwelijkheidaanduiding"),
        "types_field": "informatieobjecttypen",
        "_autorisatie_type_field": "informatieobjecttype",
        "verbose_name": _("informatieobjecttype"),
    },
    ComponentTypes.brc: {
        "required": ("related_type_selection",),
        "types_field": "besluittypen",
        "_autorisatie_type_field": "besluittype",
        "verbose_name": _("besluittype"),
    },
}


def get_scope_choices() -> List[Tuple[str, str]]:
    labels = {scope.label for scope in SCOPE_REGISTRY if not scope.children}.union(
        {SCOPE_NOTIFICATIES_CONSUMEREN_LABEL, SCOPE_NOTIFICATIES_PUBLICEREN_LABEL}
    )
    labels = sorted(labels)
    return list(zip(labels, labels))


class AutorisatieForm(forms.Form):
    component = forms.ChoiceField(
        label=_("component"),
        required=True,
        help_text=_("Component waarin deze autorisatie van toepassing is."),
        choices=ComponentTypes.choices,
        widget=forms.RadioSelect,
    )
    scopes = forms.MultipleChoiceField(
        label=_("scopes"),
        required=True,
        help_text=_("Scopes die van toepassing zijn binnen deze autorisatie"),
        choices=get_scope_choices,
        widget=forms.CheckboxSelectMultiple,
    )

    related_type_selection = forms.ChoiceField(
        label=_("{verbose_name}"),
        required=False,
        help_text=_(
            "Kies hoe je gerelateerde typen wil aanduiden. "
            "De toegekende scopes zijn enkel van toepassing op objecten van "
            "dit/deze specifieke {verbose_name_plural}"
        ),
        choices=RelatedTypeSelectionMethods.choices,
        widget=forms.RadioSelect,
    )

    vertrouwelijkheidaanduiding = forms.ChoiceField(
        label=_("maximale vertrouwelijkheidaanduiding"),
        required=False,
        help_text=_(
            "De maximale vertrouwelijkheidaanduiding waartoe consumers toegang hebben. "
            "Indien objecten van het betreffende {verbose_name} een striktere "
            "vertrouwelijkheidaanduiding hebben, dan zijn deze objecten niet "
            "toegangelijk voor de consumer."
        ),
        choices=VertrouwelijkheidsAanduiding.choices,
        widget=forms.RadioSelect,
    )

    zaaktypen = forms.ModelMultipleChoiceField(
        label=_("zaaktypen"),
        required=False,
        help_text=_("De zaaktypen waarop deze autorisatie van toepassing is."),
        queryset=ZaakType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    informatieobjecttypen = forms.ModelMultipleChoiceField(
        label=_("zaaktypen"),
        required=False,
        help_text=_("De zaaktypen waarop deze autorisatie van toepassing is."),
        queryset=InformatieObjectType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    besluittypen = forms.ModelMultipleChoiceField(
        label=_("zaaktypen"),
        required=False,
        help_text=_("De zaaktypen waarop deze autorisatie van toepassing is."),
        queryset=BesluitType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    def clean(self):
        super().clean()

        component = self.cleaned_data.get("component")

        # didn't pass validation, can't do anything else as it all relies on this
        # field
        if not component:
            return

        self._validate_scopes(component)
        self._validate_required_fields(component)

    def _validate_scopes(self, component: str):
        scopes = self.cleaned_data.get("scopes")
        # can't do anything if there are no scopes selected
        if scopes is None:
            return

        valid_prefixes = COMPONENT_TO_PREFIXES_MAP[component]
        invalid_scopes = [
            scope
            for scope in scopes
            if not any(scope.startswith(prefix) for prefix in valid_prefixes)
        ]

        if invalid_scopes:
            error = forms.ValidationError(
                _(
                    "De volgende scopes zijn geen geldige keuzes voor deze component: {scopes}"
                ).format(scopes=", ".join(invalid_scopes)),
                code="invalid",
            )
            self.add_error("scopes", error)

    def _validate_required_fields(self, component: str):
        _field_info = COMPONENT_TO_FIELDS_MAP.get(component)
        if _field_info is None:
            return

        expected_fields = _field_info["required"]
        missing = [
            field for field in expected_fields if not self.cleaned_data.get(field)
        ]

        for field in missing:
            error = forms.ValidationError(
                _("Je moet een keuze opgeven voor het veld: {field}").format(
                    field=field
                ),
                code="required",
            )
            self.add_error(field, error)

        if "related_type_selection" not in expected_fields:
            return

        related_type_selection = self.cleaned_data.get("related_type_selection")
        if related_type_selection != RelatedTypeSelectionMethods.manual_select:
            return

        # check that values for the typen have been selected manually
        types_field = _field_info["types_field"]
        if not self.cleaned_data.get(types_field):
            error = forms.ValidationError(
                _("Je moet minimaal 1 {verbose_name} kiezen").format(
                    verbose_name=_field_info["verbose_name"]
                ),
                code="required",
            )
            self.add_error(types_field, error)

    def save(self, applicatie: Applicatie, request, commit=True):
        """
        Save the Autorisatie data into the right Autorisatie objects.

        The form essentially condenses a bunch of fields, e.g. for each
        included 'zaaktype' an Autorisatie object is created.
        """
        if not commit:
            return

        # forms beyond initial data that haven't changed -> nothing to do
        if not self.has_changed() and not self.initial:
            return

        # Fixed fields
        component = self.cleaned_data["component"]
        scopes = self.cleaned_data["scopes"]

        # dependent fields
        vertrouwelijkheidaanduiding = self.cleaned_data.get(
            "vertrouwelijkheidaanduiding", ""
        )

        related_type_selection = self.cleaned_data.get("related_type_selection")
        types = None
        if related_type_selection:
            _field_info = COMPONENT_TO_FIELDS_MAP[component]

            # pick the entire queryset and install a handler for future objects
            if (
                related_type_selection
                == RelatedTypeSelectionMethods.all_current_and_future
            ):
                types = self.fields[_field_info["types_field"]].queryset
                applicatie.autorisatie_specs.update_or_create(
                    component=component,
                    defaults={
                        "scopes": scopes,
                        "max_vertrouwelijkheidaanduiding": vertrouwelijkheidaanduiding,
                    },
                )

            # pick the entire queryset
            elif related_type_selection == RelatedTypeSelectionMethods.all_current:
                types = self.fields[_field_info["types_field"]].queryset
            # only pick a queryset of the explicitly selected objects
            elif related_type_selection == RelatedTypeSelectionMethods.manual_select:
                types = self.cleaned_data[_field_info["types_field"]]

        autorisatie_kwargs = {
            "applicatie": applicatie,
            "component": component,
            "scopes": scopes,
        }

        if types is None:
            Autorisatie.objects.create(**autorisatie_kwargs)
        else:
            autorisaties = []
            for _type in types:
                data = autorisatie_kwargs.copy()
                url = request.build_absolute_uri(_type.get_absolute_api_url())
                data[_field_info["_autorisatie_type_field"]] = url
                autorisaties.append(
                    Autorisatie(
                        max_vertrouwelijkheidaanduiding=vertrouwelijkheidaanduiding,
                        **data
                    )
                )
            Autorisatie.objects.bulk_create(autorisaties)


class AutorisatieBaseFormSet(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.applicatie = kwargs.pop("applicatie")
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def save(self, commit=True):
        # use the API representation to figure out if there were any changes
        old_version = get_applicatie_serializer(
            self.applicatie, request=self.request
        ).data

        self.applicatie.autorisaties.all().delete()
        for form in self.forms:
            form.save(applicatie=self.applicatie, request=self.request, commit=commit)

        new_version = get_applicatie_serializer(
            self.applicatie, request=self.request
        ).data

        if not versions_equivalent(old_version, new_version):
            send_applicatie_changed_notification(self.applicatie, new_version)


# TODO: validate overlap zaaktypen between different auths
# TODO: support external zaaktypen
AutorisatieFormSet = forms.formset_factory(
    AutorisatieForm, extra=1, formset=AutorisatieBaseFormSet
)

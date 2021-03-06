# Generated by Django 2.2.4 on 2019-11-25 16:38

from django.db import migrations, models
import django.db.models.deletion
import django_loose_fk.fields


class Migration(migrations.Migration):

    dependencies = [
        ("zaken", "0011_auto_20191125_1635"),
    ]

    operations = [
        migrations.AddField(
            model_name="zaak",
            name="zaaktype",
            field=django_loose_fk.fields.FkOrURLField(
                fk_field="_zaaktype", url_field="_zaaktype_url"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="zaak",
            name="_zaaktype",
            field=models.ForeignKey(
                blank=True,
                help_text="URL-referentie naar het ZAAKTYPE (in de Catalogi API).",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="catalogi.ZaakType",
            ),
        ),
        migrations.AddConstraint(
            model_name="zaak",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        models.Q(_negated=True, _zaaktype__isnull=True),
                        ("_zaaktype_url", ""),
                    ),
                    models.Q(
                        ("_zaaktype__isnull", True),
                        models.Q(_negated=True, _zaaktype_url=""),
                    ),
                    _connector="OR",
                ),
                name="_zaaktype_or__zaaktype_url_filled",
            ),
        ),
    ]

# Generated by Django 2.2.4 on 2019-11-26 16:02

from django.db import migrations, models
import django.db.models.deletion
import django_loose_fk.fields


class Migration(migrations.Migration):

    dependencies = [
        ("documenten", "0010_auto_20191126_1548"),
    ]

    operations = [
        migrations.AddField(
            model_name="enkelvoudiginformatieobject",
            name="informatieobjecttype",
            field=django_loose_fk.fields.FkOrURLField(
                fk_field="_informatieobjecttype", url_field="_informatieobjecttype_url",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="enkelvoudiginformatieobject",
            name="_informatieobjecttype",
            field=models.ForeignKey(
                blank=True,
                help_text="URL-referentie naar het INFORMATIEOBJECTTYPE (in de Catalogi API).",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="catalogi.InformatieObjectType",
            ),
        ),
        migrations.AddConstraint(
            model_name="enkelvoudiginformatieobject",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        models.Q(_informatieobjecttype__isnull=True, _negated=True),
                        ("_informatieobjecttype_url", ""),
                    ),
                    models.Q(
                        ("_informatieobjecttype__isnull", True),
                        models.Q(_informatieobjecttype_url="", _negated=True),
                    ),
                    _connector="OR",
                ),
                name="_informatieobjecttype_or__informatieobjecttype_url_filled",
            ),
        ),
    ]

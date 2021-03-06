# Generated by Django 2.2.4 on 2019-11-22 14:11

from django.db import migrations

import openzaak.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ("zaken", "0009_auto_20191017_1517"),
    ]

    operations = [
        migrations.AlterField(
            model_name="zaak",
            name="verlenging_duur",
            field=openzaak.utils.fields.DurationField(
                blank=True,
                help_text="Het aantal kalenderdagen waarmee de doorlooptijd van de behandeling van de ZAAK is verlengd (of verkort) ten opzichte van de eerder gecommuniceerde doorlooptijd.",
                null=True,
                verbose_name="duur verlenging",
            ),
        ),
    ]

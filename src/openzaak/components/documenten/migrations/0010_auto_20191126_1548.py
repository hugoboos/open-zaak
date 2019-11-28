# Generated by Django 2.2.4 on 2019-11-26 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalogi", "0012_auto_20191122_1414"),
        ("documenten", "0009_auto_20191107_1028"),
    ]

    operations = [
        migrations.RenameField(
            model_name="enkelvoudiginformatieobject",
            old_name="informatieobjecttype",
            new_name="_informatieobjecttype",
        ),
        migrations.AddField(
            model_name="enkelvoudiginformatieobject",
            name="_informatieobjecttype_url",
            field=models.URLField(
                blank=True,
                help_text="URL-referentie naar extern INFORMATIEOBJECTTYPE (in een andere Catalogi API).",
                max_length=1000,
                verbose_name="extern informatieobjecttype",
            ),
        ),
    ]

# Generated by Django 2.2.4 on 2019-11-12 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("catalogi", "0007_auto_20191112_0903"),
    ]

    operations = [
        migrations.RenameField(
            model_name="zaaktype",
            old_name="zaaktype_identificatie",
            new_name="identificatie",
        ),
    ]

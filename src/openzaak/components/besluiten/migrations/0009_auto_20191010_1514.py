# Generated by Django 2.2.4 on 2019-10-10 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("besluiten", "0008_auto_20190924_1339")]

    operations = [
        migrations.RenameField(model_name="besluit", old_name="zaak", new_name="_zaak")
    ]

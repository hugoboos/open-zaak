# Generated by Django 2.2.4 on 2019-08-22 13:25

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("besluiten", "0003_auto_20190820_0945"),
        ("zaken", "0004_auto_20190820_0945"),
        ("documenten", "0004_auto_20190820_0945"),
    ]

    operations = [
        migrations.CreateModel(
            name="ObjectInformatieObject",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        help_text="Unieke resource identifier (UUID4)",
                        unique=True,
                    ),
                ),
                (
                    "object_type",
                    models.CharField(
                        choices=[("besluit", "Besluit"), ("zaak", "Zaak")],
                        help_text="Het type van het gerelateerde OBJECT.",
                        max_length=100,
                        verbose_name="objecttype",
                    ),
                ),
                (
                    "besluit",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="besluiten.Besluit",
                    ),
                ),
                (
                    "informatieobject",
                    models.ForeignKey(
                        help_text="URL-referentie naar het INFORMATIEOBJECT.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="documenten.EnkelvoudigInformatieObjectCanonical",
                    ),
                ),
                (
                    "zaak",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="zaken.Zaak",
                    ),
                ),
            ],
            options={
                "verbose_name": "objectinformatieobject",
                "verbose_name_plural": "objectinformatieobjecten",
            },
        ),
        migrations.AddConstraint(
            model_name="objectinformatieobject",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("besluit__isnull", True),
                        ("object_type", "zaak"),
                        ("zaak__isnull", False),
                    ),
                    models.Q(
                        ("besluit__isnull", False),
                        ("object_type", "besluit"),
                        ("zaak__isnull", True),
                    ),
                    _connector="OR",
                ),
                name="check_type",
            ),
        ),
    ]

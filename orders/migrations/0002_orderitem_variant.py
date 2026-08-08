from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="variant_label",
            field=models.CharField(default="To'liq flakon", max_length=50, verbose_name="Tanlangan hajm"),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="variant_volume_ml",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Hajm (ml)"),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_sitesettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="sell_by_ml",
            field=models.BooleanField(default=False, verbose_name="Ml bo'yicha sotiladi"),
        ),
        migrations.AddField(
            model_name="product",
            name="price_10ml",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name="10 ml narxi ($)"),
        ),
        migrations.AddField(
            model_name="product",
            name="price_20ml",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name="20 ml narxi ($)"),
        ),
        migrations.AddField(
            model_name="product",
            name="price_30ml",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name="30 ml narxi ($)"),
        ),
        migrations.AddField(
            model_name="product",
            name="price_40ml",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name="40 ml narxi ($)"),
        ),
        migrations.AddField(
            model_name="product",
            name="price_50ml",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name="50 ml narxi ($)"),
        ),
    ]

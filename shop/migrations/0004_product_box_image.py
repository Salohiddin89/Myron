from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0003_product_ml_prices"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="box_image",
            field=models.ImageField(
                blank=True,
                help_text="Kursor mahsulot ustiga kelganda ko'rsatiladigan karobka rasmi.",
                null=True,
                upload_to="products/boxes/",
                verbose_name="Karobka rasmi",
            ),
        ),
    ]

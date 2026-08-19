from django.db import migrations, models
from django.db.models import deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0004_product_box_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="show_user_rating",
            field=models.BooleanField(
                default=True,
                verbose_name="User Rating blokini ko'rsatish",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="show_when_to_wear",
            field=models.BooleanField(
                default=True,
                verbose_name="When to wear blokini ko'rsatish",
            ),
        ),
        migrations.CreateModel(
            name="ProductVote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visitor_key", models.CharField(max_length=128)),
                (
                    "vote_type",
                    models.CharField(
                        choices=[
                            ("rating", "User Rating"),
                            ("wear", "When to wear"),
                        ],
                        max_length=12,
                    ),
                ),
                ("choice", models.CharField(max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=deletion.CASCADE,
                        related_name="votes",
                        to="shop.product",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["product", "vote_type", "choice"],
                        name="shop_product_vote_lookup_idx",
                    )
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("product", "visitor_key", "vote_type"),
                        name="unique_product_vote_visitor_type",
                    )
                ],
            },
        ),
    ]

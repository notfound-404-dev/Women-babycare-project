from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    AGE_GROUP_CHOICES = [
        ("all", "All Ages"),
        ("0-6", "0-6 months"),
        ("6-12", "6-12 months"),
        ("1-3", "1-3 years"),
        ("3+", "3+ years"),
        ("mother", "Mother Care"),
    ]

    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    baby_age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES, default="all")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

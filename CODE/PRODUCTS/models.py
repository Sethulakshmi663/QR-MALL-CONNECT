from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rack_no = models.CharField(max_length=50, blank=True)
    floor = models.CharField(max_length=50)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Offer(models.Model):
    product = models.ForeignKey(Product, related_name="offers", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    discount_percent = models.PositiveIntegerField()
    valid_until = models.DateField()

    def __str__(self):
        return f"{self.title} for {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Anonymous")
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐"


class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    referrer = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Product View"
        verbose_name_plural = "Product Views"
        indexes = [
            models.Index(fields=['product', 'viewed_at']),
            models.Index(fields=['viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.product.name} viewed at {self.viewed_at}"


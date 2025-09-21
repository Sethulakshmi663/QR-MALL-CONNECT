from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Offer, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'floor', 'available', 'image_preview', 'created_at']
    list_filter = ['category', 'available', 'floor', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'available']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    actions = ['mark_as_available', 'mark_as_unavailable', 'bulk_price_update']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'available')
        }),
        ('Location', {
            'fields': ('floor', 'rack_no', 'location')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image"
    
    # Bulk actions
    def mark_as_available(self, request, queryset):
        updated = queryset.update(available=True)
        self.message_user(request, f'{updated} products marked as available.')
    mark_as_available.short_description = "Mark selected products as available"
    
    def mark_as_unavailable(self, request, queryset):
        updated = queryset.update(available=False)
        self.message_user(request, f'{updated} products marked as unavailable.')
    mark_as_unavailable.short_description = "Mark selected products as unavailable"
    
    def bulk_price_update(self, request, queryset):
        # This would typically redirect to a form for price updates
        selected = queryset.count()
        self.message_user(request, f'{selected} products selected for bulk price update. Use the list_editable feature to update prices quickly.')
    bulk_price_update.short_description = "Prepare for bulk price update"

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'product', 'discount_percent', 'valid_until']
    list_filter = ['valid_until', 'discount_percent']
    search_fields = ['title', 'product__name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['name', 'product__name', 'comment']
    readonly_fields = ['created_at']

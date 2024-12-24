# engraving/admin.py
from django.contrib import admin
from .models import Supplier, Material, Glass, Engraving, ImageUpload

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('material_name',)

@admin.register(Glass)
class GlassAdmin(admin.ModelAdmin):
    list_display = ('glass_name', 'glass_index', 'material', 'supplier', 'category')
    list_filter = ('category', 'supplier', 'material')
    search_fields = ('glass_name', 'glass_index')

@admin.register(Engraving)
class EngravingAdmin(admin.ModelAdmin):
    list_display = ('engraving_code', 'glass', 'confidence')

@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    list_display = ('image', 'uploaded_at', 'analyzed')
    list_filter = ('analyzed',)

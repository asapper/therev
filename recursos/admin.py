from django.contrib import admin

from .models import Finishing, Material, Paper


class FinishingAdmin(admin.ModelAdmin):
    list_display = ('id', 'finishing_name', 'finishing_price')
    search_fields = ['finishing_name']


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'material_name', 'material_price')
    search_fields = ['material_name']


class PaperAdmin(admin.ModelAdmin):
    list_display = ('id', 'paper_name', 'paper_width', 'paper_length',
                    'paper_price')
    search_fields = ['paper_name']


admin.site.register(Finishing, FinishingAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Paper, PaperAdmin)

from django.contrib import admin
from .models import FarmStory, FarmStoryLike


@admin.register(FarmStory)
class FarmStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'farmer_name', 'like_count', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    list_editable = ('is_approved',)
    search_fields = ('title', 'farmer_name')


@admin.register(FarmStoryLike)
class FarmStoryLikeAdmin(admin.ModelAdmin):
    list_display = ('story', 'customer', 'created_at')

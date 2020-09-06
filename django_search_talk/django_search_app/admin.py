from django.contrib import admin
from .models import FTSReview

@admin.register(FTSReview)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_summary', 'review_time', 'review_help_help', 'review_help_total')
    list_filter = ('review_score', 'review_time')
    search_fields = ('review_text', 'review_summary')
    date_hierarchy = 'review_time'


from django.core import urlresolvers
from django.utils.translation import ugettext as _
from django.contrib import admin
from reviews.models import Review, ReviewSegment, Category, CategorySegment

class ReviewSegmentInline(admin.TabularInline):
    model = ReviewSegment

    """ no manual alteration of the segments amount, so no deletion and no
    extra fields. """
    extra = 0
    can_delete = False

    """ prevents that new segments can be added. The segments are defined
    in the form, and thats it. """
    max_num = 0

    """ since alterations to the segments amount is disabled, manual category
    changing of the existing segments is also not allowed """
    readonly_fields = ('segment',)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'content_object')

    raw_id_fields = ('user',)

    inlines = [
        ReviewSegmentInline,
    ]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'segment_link')

    search_fields = ['code']

    def segment_link(self, obj):
      return '<a href="../categorysegment/?q=&category__id__exact=%s">%s</a>' % (str(obj.id), _('Show all segments'))
    segment_link.allow_tags = True

class CategorySegmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'category_link')
    list_filter = ('title', 'category')
    list_select_related = True

    def category_link(self, obj):
      return '<a href="%s">%s</a>' % (urlresolvers.reverse('admin:reviews_category_change', args=(obj.category.id,)), obj.category.code)
    category_link.allow_tags = True

    search_fields = ['title', 'category__code']

admin.site.register(Review, ReviewAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CategorySegment, CategorySegmentAdmin)

from django.contrib import admin
from lessons.models import User, Request, Booking, Child

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'email','first_name', 'last_name', 'role', 'is_active'
    ]

admin.site.register(Request)
admin.site.register(Booking)
admin.site.register(Child)
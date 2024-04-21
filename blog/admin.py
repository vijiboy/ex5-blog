from django.contrib import admin
from .models import (
    Post,
    Property,
    PropertyUnit,
    PropertyOwnership,
    RentalLease,
    Transaction,
)


# Register your models here.
admin.site.register(Post)
admin.site.register(PropertyUnit)
admin.site.register(Property)
admin.site.register(PropertyOwnership)
admin.site.register(RentalLease)
admin.site.register(Transaction)

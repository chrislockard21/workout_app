from django.contrib import admin
from .models import Log, Set, SetHistory, LogHistory

# Register your models here.
admin.site.register(Log)
admin.site.register(Set)
admin.site.register(SetHistory)
admin.site.register(LogHistory)

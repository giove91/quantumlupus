from django.contrib import admin

from game.models import *

admin.site.register(Player)
admin.site.register(Game)
admin.site.register(Village)
admin.site.register(Status)
admin.site.register(Action)
admin.site.register(Log)


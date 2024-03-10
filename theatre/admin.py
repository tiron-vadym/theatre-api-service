from django.contrib import admin

from .models import (
    Play,
    Actor,
    Genre,
    TheatreHall,
    Performance,
    Reservation,
    Ticket,
)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    inlines = (TicketInline, )


admin.site.register(Play)
admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(TheatreHall)
admin.site.register(Performance)
admin.site.register(Ticket)

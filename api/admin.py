from django.contrib import admin
from .models import Wallet, Match, League, Transaction, LeagueMember

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team_a', 'team_b', 'match_time', 'stage')

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'entry_fee', 'prize_pool', 'managers', 'is_public')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'created_at')
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Wallet, Match, League, LeagueMember, Transaction
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seeds initial data for Cutthroat Cup'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Clear existing data (Optional, but good for fresh start)
        Transaction.objects.all().delete()
        LeagueMember.objects.all().delete()
        League.objects.all().delete()
        Match.objects.all().delete()
        Wallet.objects.all().delete()

        # 2. Create Demo User (Shannon)
        user, created = User.objects.get_or_create(username='shannon')
        if created:
            user.set_password('password123')
            user.save()
        
        # Create Wallet
        wallet, _ = Wallet.objects.get_or_create(user=user)
        wallet.balance = 184.00
        wallet.save()

        # 3. Create Matches (World Cup 2026 Theme)
        now = timezone.now()
        matches = [
            {"team_a": "Brazil", "team_b": "Spain", "flag_a": "🇧🇷", "flag_b": "🇪🇸", "stage": "Round of 16", "time": now + timedelta(days=1, hours=3)},
            {"team_a": "Netherlands", "team_b": "Argentina", "flag_a": "🇳🇱", "flag_b": "🇦🇷", "stage": "Round of 16", "time": now + timedelta(days=2, hours=1)},
            {"team_a": "France", "team_b": "Portugal", "flag_a": "🇫🇷", "flag_b": "🇵🇹", "stage": "Round of 16", "time": now + timedelta(days=3, hours=4)},
            {"team_a": "England", "team_b": "Germany", "flag_a": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "flag_b": "🇩🇪", "stage": "Round of 16", "time": now + timedelta(days=4, hours=2)},
            {"team_a": "Brazil", "team_b": "Argentina", "flag_a": "🇧🇷", "flag_b": "🇦🇷", "stage": "Quarter Finals", "time": now + timedelta(days=5, hours=3)},
        ]
        
        for m in matches:
            Match.objects.create(
                team_a=m["team_a"], team_b=m["team_b"],
                flag_a=m["flag_a"], flag_b=m["flag_b"],
                stage=m["stage"], match_time=m["time"]
            )
        self.stdout.write(f"Created {len(matches)} matches")

        # 4. Create Leagues
        leagues_data = [
            {"name": "World Cup Degens", "entry": 10.00, "prize": 18750.00, "max": 24, "is_public": True},
            {"name": "Office Legends", "entry": 15.00, "prize": 12450.00, "max": 12, "is_public": False},
            {"name": "Pod Bashers", "entry": 10.00, "prize": 12200.00, "max": 8, "is_public": False},
            {"name": "Global Cup 2026", "entry": 5.00, "prize": 500.00, "max": 100, "is_public": True},
            {"name": "FIFA Fanatics", "entry": 20.00, "prize": 5000.00, "max": 20, "is_public": True},
        ]

        created_leagues = []
        for l in leagues_data:
            league = League.objects.create(
                name=l["name"], entry_fee=l["entry"], prize_pool=l["prize"],
                max_managers=l["max"], is_public=l["is_public"],
                managers=random.randint(1, l["max"] - 1) # Random managers joined
            )
            created_leagues.append(league)
        self.stdout.write(f"Created {len(leagues_data)} leagues")

        # 5. Make Shannon join one league (World Cup Degens)
        wc_degens = League.objects.get(name="World Cup Degens")
        LeagueMember.objects.create(user=user, league=wc_degens)
        wc_degens.managers += 1
        wc_degens.save()

        # 6. Create Transactions (Recent Activity)
        transactions = [
            {"user": user, "amount": 200.00, "type": "WINNINGS", "desc": "Won pool in Office Legends"},
            {"user": user, "amount": 10.00, "type": "ENTRY_FEE", "desc": "Joined World Cup Degens"},
            {"user": user, "amount": 150.00, "type": "WINNINGS", "desc": "Match day winnings"},
        ]
        for t in transactions:
            Transaction.objects.create(
                user=t["user"], amount=t["amount"], 
                transaction_type=t["type"], description=t["desc"]
            )
        
        self.stdout.write(self.style.SUCCESS("Successfully seeded all data!"))
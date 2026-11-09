from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=184.00)

    def __str__(self):
        return f"{self.user.username} - ${self.balance}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email = models.EmailField(blank=True)
    favorite_team = models.CharField(max_length=50, default="Brazil")

    def __str__(self):
        return self.user.username

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    match_reminders = models.BooleanField(default=True)
    waiver_results = models.BooleanField(default=True)
    league_invites = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} Settings"

class Match(models.Model):
    team_a = models.CharField(max_length=50)
    team_b = models.CharField(max_length=50)
    match_time = models.DateTimeField()
    stage = models.CharField(max_length=50, default="Round of 16")
    flag_a = models.CharField(max_length=10, blank=True)
    flag_b = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.team_a} vs {self.team_b}"

class League(models.Model):
    name = models.CharField(max_length=100)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2)
    managers = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)
    max_managers = models.IntegerField(default=10)

    def __str__(self):
        return self.name

class LeagueMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_leagues')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'league')

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('ENTRY_FEE', 'Entry Fee'),
        ('WINNINGS', 'Winnings'),
        ('DEPOSIT', 'Deposit'),
        ('DRAFT_FEE', 'Draft Fee')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ${self.amount}"

class DraftedTeam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drafted_teams')
    team_name = models.CharField(max_length=50)
    flag = models.CharField(max_length=10)

    class Meta:
        unique_together = ('user', 'team_name')

class WaiverBid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waivers')
    team_name = models.CharField(max_length=50)
    flag = models.CharField(max_length=10)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

# Auto-create Wallet, Profile, Settings when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
        UserProfile.objects.create(user=instance, email=instance.email)
        UserSettings.objects.create(user=instance)
from rest_framework import serializers
from .models import Wallet, Match, League, LeagueMember, Transaction, UserProfile, UserSettings, DraftedTeam, WaiverBid
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance']

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'favorite_team']

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        exclude = ['user']

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class LeagueSerializer(serializers.ModelSerializer):
    is_joined = serializers.SerializerMethodField()
    class Meta:
        model = League
        fields = '__all__'

    def get_is_joined(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LeagueMember.objects.filter(user=request.user, league=obj).exists()
        return False

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class DraftedTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftedTeam
        fields = '__all__'

class WaiverBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaiverBid
        fields = ['id', 'team_name', 'flag', 'bid_amount', 'created_at'] # 'user' ozhivaakki
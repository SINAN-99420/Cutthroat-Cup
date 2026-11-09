from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal # Decimal error fix
from .models import *
from .serializers import *

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_data(request):
    user = request.user
    wallet, _ = Wallet.objects.get_or_create(user=user)
    my_leagues = League.objects.filter(members__user=user)
    upcoming_matches = Match.objects.all().order_by('match_time')[:2]

    return Response({
        'user': UserSerializer(user).data,
        'wallet': WalletSerializer(wallet).data,
        'my_leagues': LeagueSerializer(my_leagues, many=True, context={'request': request}).data,
        'upcoming_matches': MatchSerializer(upcoming_matches, many=True).data,
    })

class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = League.objects.filter(is_public=True)
    serializer_class = LeagueSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        league = self.get_object()
        user = request.user
        wallet, _ = Wallet.objects.get_or_create(user=user)

        if LeagueMember.objects.filter(user=user, league=league).exists():
            return Response({"error": "Already joined."}, status=status.HTTP_400_BAD_REQUEST)

        if wallet.balance < league.entry_fee:
            return Response({"error": "Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)

        wallet.balance -= league.entry_fee
        wallet.save()
        LeagueMember.objects.create(user=user, league=league)
        Transaction.objects.create(user=user, amount=league.entry_fee, transaction_type='ENTRY_FEE', description=f"Joined {league.name}")
        league.managers += 1
        league.save()

        return Response({"message": f"Successfully joined {league.name}!", "new_balance": str(wallet.balance)})

class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all().order_by('match_time')
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def account_view(request):
    # Ithu illenkil auto aayi create aakum (User has no profile fix)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        return Response(UserProfileSerializer(profile).data)
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def settings_view(request):
    # Ithu illenkil auto aayi create aakum (User has no settings fix)
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        return Response(UserSettingsSerializer(settings_obj).data)
    elif request.method == 'PUT':
        serializer = UserSettingsSerializer(settings_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_view(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return Response(TransactionSerializer(transactions, many=True).data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def draft_view(request):
    if request.method == 'GET':
        teams = DraftedTeam.objects.filter(user=request.user)
        return Response(DraftedTeamSerializer(teams, many=True).data)
    
    if request.method == 'POST':
        team_name = request.data.get('team_name')
        flag = request.data.get('flag')
        draft_fee = Decimal('50.00') # Ithu Decimal aakki maatti (Error fix)
        
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        if wallet.balance < draft_fee:
            return Response({"error": "Insufficient funds to draft."}, status=status.HTTP_400_BAD_REQUEST)
        
        if DraftedTeam.objects.filter(user=request.user, team_name=team_name).exists():
             return Response({"error": "Already drafted."}, status=status.HTTP_400_BAD_REQUEST)

        wallet.balance -= draft_fee
        wallet.save()
        DraftedTeam.objects.create(user=request.user, team_name=team_name, flag=flag)
        Transaction.objects.create(user=request.user, amount=draft_fee, transaction_type='DRAFT_FEE', description=f"Drafted {team_name}")
        
        return Response({"message": f"Drafted {team_name}!"})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def waivers_view(request):
    if request.method == 'GET':
        waivers = WaiverBid.objects.filter(user=request.user)
        return Response(WaiverBidSerializer(waivers, many=True).data)
        
    if request.method == 'POST':
        serializer = WaiverBidSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Bid placed successfully!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conflict_view(request):
    drafted_teams = [t.team_name for t in DraftedTeam.objects.filter(user=request.user)]
    conflicts = []
    for match in Match.objects.all():
        if match.team_a in drafted_teams and match.team_b in drafted_teams:
            conflicts.append(MatchSerializer(match).data)
    return Response(conflicts)

from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # User create cheyyunnu (Wallet, Profile, Settings ellam signal vazhi auto aayi create aakum)
    user = User.objects.create_user(username=username, email=email, password=password)
    
    # Token create cheyyunnu
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "message": "User registered successfully!",
        "token": token.key,
        "username": user.username
    }, status=status.HTTP_201_CREATED)
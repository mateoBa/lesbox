from rest_framework import serializers
from api.models import User, Party, Track

__author__ = 'agusx1211'


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_name', 'spotify_id', 'email', 'last_token_spotify', 'account_type')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_name', 'spotify_id', 'get_current_luck', 'email')


class PartySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Party
        fields = ('id', 'owner', 'name', 'members')


class TrackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Track
        fields = (
            'id', 'user', 'get_party_id', 'spotify_track_id', 'name', 'duration_ms', 'explicit', 'preview_url', 'href',
            'popularity', 'uri', 'priority', 'artist_name')


class PartySecretSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Party
        fields = ('id', 'owner', 'name', 'members', 'secret')


class PartySecretComplexSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    get_total_tracks = TrackSerializer(many=True, read_only=True)
    get_last_played_track = TrackSerializer(read_only=True)

    class Meta:
        model = Party
        fields = ('id', 'owner', 'name', 'members', 'secret', 'get_last_played_track', 'get_total_tracks')

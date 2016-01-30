import json
from django.core import serializers
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from api.models import User, Party, Track
from django.views.decorators.csrf import csrf_exempt
from api.serializers import AccountSerializer, PartySerializer, TrackSerializer, PartySecretSerializer, \
    PartySecretComplexSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def login(request):
    try:
        received_json_data = json.loads(request.body)
        u = User(spotify_id=received_json_data['spotifyId'])
        u.account_type = received_json_data['account_type']
        u.user_name = received_json_data["username"]
        u.email = received_json_data["email"]
    except ValueError:
        return HttpResponse("Inavlid Json", status=403)

    if u.last_token_spotify != received_json_data["spotifyToken"]:
        u.last_token_spotify = received_json_data["spotifyToken"]
        if u.check_token_spotify():
            u.save()
            serializer = AccountSerializer(u, many=False)
            return JSONResponse(serializer.data)

    return HttpResponse("Spotify user not valid", status=400)


@csrf_exempt
def get_user_parties(request):
    try:
        token = request.META["HTTP_AUTHORIZATION"]

        received_json_data = json.loads(request.body)
        user = User.objects.get(spotify_id=received_json_data['userId'])
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)

    if not user.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    parties = Party.get_parties_with(user)
    serializer = PartySecretSerializer(parties, many=True)
    return JSONResponse(serializer.data, status=200)


@csrf_exempt
def create_party(request):
    try:
        token = request.META["HTTP_AUTHORIZATION"]

        received_json_data = json.loads(request.body)
        owner = User.objects.get(spotify_id=received_json_data['userId'])
        party_name = received_json_data['partyName']
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)
    except KeyError:
        return HttpResponse("Inavlid Json", status=400)

    if not owner.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    party = Party.create_party(owner, party_name)
    party.save()

    party.members.add(owner)
    party.save()

    serializer = PartySecretSerializer(party, many=False)
    return JSONResponse(serializer.data, status=201)


@csrf_exempt
def join_party(request):
    try:
        token = request.META["HTTP_AUTHORIZATION"]

        received_json_data = json.loads(request.body)
        user = User.objects.get(spotify_id=received_json_data['userId'])
        party = Party.objects.get(id=received_json_data['partyId'])
        secret = received_json_data['party_secret']
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)
    except KeyError:
        return HttpResponse("Inavlid Json", status=400)

    if not user.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    if party.validate_secret(secret):
        serializer = PartySecretSerializer(party, many=False)
        user.join_party(party)
        party.save()
        return JSONResponse(serializer.data, status=200)
    else:
        return HttpResponse("Secret incorrecto", status=401)


@csrf_exempt
def update_tracks(request):
    try:
        token = request.META["HTTP_AUTHORIZATION"]

        received_json_data = json.loads(request.body)
        received_json_tracks = received_json_data['tracks']
        owner = User.objects.get(spotify_id=received_json_data['userId'])
        party = Party.objects.get(id=received_json_data['partyId'])
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)

    if not owner.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    for _track in received_json_tracks:
        try:
            "If track exist update priority"
            track = Track.objects.get(id=_track["id"])
            track.priority = _track["priority"]
            track.save()
        except (KeyError, ValueError) as e:
            "Si no existe no se hace nada"

    return return_all_tracks(party, owner)


@csrf_exempt
def get_next_track(request):
    try:
        token = request.META["HTTP_AUTHORIZATION"]

        received_json_data = json.loads(request.body)
        owner = User.objects.get(spotify_id=received_json_data['userId'])
        party = Party.objects.get(id=received_json_data['partyId'])
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)

    if not owner.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    if party.owner != owner:
        return HttpResponse("No puedes obtener el siguiente track de una party que no te pertenece", status=401)

    track = party.get_next_track()
    if track is not None:
        serializer = TrackSerializer(track, many=False)
        return JSONResponse(serializer.data, status=200)
    else:
        return HttpResponse("null", status=200)


@csrf_exempt
def get_tracks(request):
    try:
        token = request.META["HTTP_AUTHORIZATION"]

        received_json_data = json.loads(request.body)
        owner = User.objects.get(spotify_id=received_json_data['userId'])
        party = Party.objects.get(id=received_json_data['partyId'])
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)

    if not owner.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    return return_all_tracks(party, owner)


@csrf_exempt
def del_all_tracks(request):
    try:
        token = request.META["HTTP_AUTHENTICATION"]

        received_json_data = json.loads(request.body)
        owner = User.objects.get(spotifyId=received_json_data['userId'])
        party = Party.objects.get(id=received_json_data['partyId'])
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)

    if owner.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    Track.del_all_tracks(party, owner)
    return return_all_tracks(party, owner)


@csrf_exempt
def add_track(request):
    try:
        token = request.META["HTTP_AUTHORIZATION"]

        received_json_data = json.loads(request.body)
        received_json_tracks = received_json_data['tracks']
        owner = User.objects.get(spotify_id=received_json_data['userId'])
        party = Party.objects.get(id=received_json_data['partyId'])
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)

    if not owner.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    for _track in received_json_tracks:
            "Create a new track"
            track = Track.create_track(owner, party, _track["spotify_track_id"], _track["name"], _track["duration_ms"],
                                       _track["explicit"], _track["preview_url"], _track["href"], _track["popularity"],
                                       _track["uri"], Track.get_last_priority(party, owner) + 1, _track["artist_name"])

            track.save()

    return return_all_tracks(party, owner)


def return_all_tracks(party, owner):
    tracks = Track.get_all_tracks(party, owner)
    serializer = TrackSerializer(tracks, many=True)
    return JSONResponse(serializer.data, status=200)


@csrf_exempt
def get_all_tracks(request):
    try:
        token = request.META["HTTP_AUTHORIZATION"]

        received_json_data = json.loads(request.body)
        user = User.objects.get(spotify_id=received_json_data['userId'])
        party = Party.objects.get(id=received_json_data['partyId'])
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)

    if not user.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    serializer = PartySecretComplexSerializer(party, many=False)
    return JSONResponse(serializer.data, status=200)


@csrf_exempt
def leave_party(request):
    try:
        token = request.META["HTTP_AUTHORIZATION"]

        received_json_data = json.loads(request.body)
        user = User.objects.get(spotify_id=received_json_data['userId'])
        party = Party.objects.get(id=received_json_data['partyId'])
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)
    except KeyError:
        return HttpResponse("Inavlid Json", status=400)

    if not user.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    user.left_party(party)
    return HttpResponse("ok", status=200)


@csrf_exempt
def del_track(request):
    try:
        token = request.META["HTTP_AUTHORIZATION"]

        received_json_data = json.loads(request.body)
        user = User.objects.get(spotify_id=received_json_data['userId'])
        track = Track.objects.get(id=received_json_data['trackId'])
    except ValueError:
        return HttpResponse("Inavlid Json", status=400)
    except KeyError:
        return HttpResponse("Inavlid Json", status=400)

    if not user.is_authenticated(token):
        return HttpResponse("No authenticated", status=403)

    if track.user.spotify_id == user.spotify_id:
        track.delete()
        return HttpResponse("ok", status=200)

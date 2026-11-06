import json
import re
import random
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import render
from .models import Pokemon
from .forms import PokemonForm
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404



def lista_pokemones(request):
    pokemones = Pokemon.objects.all()
    busqueda = request.GET.get("buscar", "").strip().lower()
    pokemon_api = None
    error_api = None

    if busqueda:
        if not re.fullmatch(r"[a-z0-9-]{1,50}", busqueda):
            error_api = "Escribe un nombre o número de Pokédex válido."
        else:
            clave_cache = f"pokeapi:pokemon:{busqueda}"
            datos = cache.get(clave_cache)

            if datos is None:
                url = f"https://pokeapi.co/api/v2/pokemon/{quote(busqueda, safe='')}"
                solicitud = Request(
                    url,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "PokedexDjango/1.0",
                    },
                )

                try:
                    with urlopen(solicitud, timeout=8) as respuesta:
                        datos = json.loads(respuesta.read().decode("utf-8"))
                    cache.set(clave_cache, datos, 60 * 60 * 24)
                except HTTPError as error:
                    if error.code == 404:
                        error_api = "No encontramos ese Pokémon en PokéAPI."
                    else:
                        error_api = "PokéAPI no pudo responder en este momento."
                except (URLError, TimeoutError, json.JSONDecodeError):
                    error_api = "No se pudo conectar con PokéAPI. Intenta de nuevo."

            if datos is not None:
                tipos_es = {
                    "bug": "bicho", "dark": "siniestro", "dragon": "dragón",
                    "electric": "eléctrico", "fairy": "hada", "fighting": "lucha",
                    "fire": "fuego", "flying": "volador", "ghost": "fantasma",
                    "grass": "planta", "ground": "tierra", "ice": "hielo",
                    "normal": "normal", "poison": "veneno", "psychic": "psíquico",
                    "rock": "roca", "steel": "acero", "water": "agua",
                }
                imagenes = datos.get("sprites", {}).get("other", {})
                imagen = imagenes.get("official-artwork", {}).get("front_default")
                pokemon_api = {
                    "numero": datos["id"],
                    "nombre": datos["name"].replace("-", " ").title(),
                    "imagen": imagen or datos.get("sprites", {}).get("front_default"),
                    "peso": round(datos["weight"] / 10, 1),
                    "elementos": [
                        tipos_es.get(tipo["type"]["name"], tipo["type"]["name"])
                        for tipo in datos.get("types", [])
                    ],
                    "habilidades": [
                        habilidad["ability"]["name"].replace("-", " ")
                        for habilidad in datos.get("abilities", [])
                    ],
                }

    return render(
        request,
        "pokemon/lista_pokemones.html",
        {
            "pokemones": pokemones,
            "busqueda": busqueda,
            "pokemon_api": pokemon_api,
            "error_api": error_api,
        },
    )


def quiz_pokemon(request):
    return render(request, "pokemon/quiz_pokemon.html")


@require_GET
def api_pregunta_quiz(request):
    tarjetas = cache.get("tcgdex:en:tarjetas-pokemon")

    if tarjetas is None:
        parametros = urlencode({
            "category": "eq:Pokemon",
            "pagination:itemsPerPage": 100,
            "pagination:page": 1,
        })
        url = f"https://api.tcgdex.net/v2/en/cards?{parametros}"
        solicitud = Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "PokedexDjango/1.0"},
        )

        try:
            with urlopen(solicitud, timeout=10) as respuesta:
                tarjetas = json.loads(respuesta.read().decode("utf-8"))
            if not isinstance(tarjetas, list):
                return JsonResponse(
                    {"error": "TCGdex devolvió una respuesta inesperada."},
                    status=502,
                )
            cache.set("tcgdex:en:tarjetas-pokemon", tarjetas, 60 * 60 * 24)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            return JsonResponse(
                {"error": "No se pudo conectar con TCGdex. Intenta de nuevo."},
                status=503,
            )

    por_nombre = {}
    for tarjeta in tarjetas:
        nombre = tarjeta.get("name")
        imagen = tarjeta.get("image")
        if nombre and imagen:
            por_nombre.setdefault(nombre, imagen)

    opciones = list(por_nombre.items())
    if len(opciones) < 4:
        return JsonResponse(
            {"error": "TCGdex no devolvió suficientes cartas para el quiz."},
            status=503,
        )

    random.shuffle(opciones)
    seleccionadas = opciones[:4]
    respuesta, imagen = seleccionadas[0]
    nombres = [nombre for nombre, _ in seleccionadas]
    random.shuffle(nombres)

    return JsonResponse({
        "imagen": f"{imagen.rstrip('/')}/low.webp",
        "opciones": nombres,
        "respuesta": respuesta,
    })


def crear_pokemon(request):
    if request.method == "POST":
        form = PokemonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("pokemon:lista")
    else:
        form = PokemonForm()

    return render(request, "pokemon/crear_pokemon.html", {"form": form})


def editar_pokemon(request, pk):
    pokemon = get_object_or_404(Pokemon, pk=pk)

    if request.method == "POST":
        form = PokemonForm(request.POST, instance=pokemon)
        if form.is_valid():
            form.save()
            return redirect("pokemon:lista")
    else:
        form = PokemonForm(instance=pokemon)

    return render(
    request,
    "pokemon/crear_pokemon.html",
    {"form": form, "titulo": "Agregar Pokémon"},
)


from django.contrib import messages

def eliminar_pokemon(request, pk):
    pokemon = get_object_or_404(Pokemon, pk=pk)

    if request.method == "POST":
        nombre = pokemon.nombre
        pokemon.delete()
        messages.success(request, f"{nombre} fue eliminado.")
        return redirect("pokemon:lista")

    return render(
        request,
        "pokemon/eliminar_pokemon.html",
        {"pokemon": pokemon},
    )

from .models import Entrenador


def lista_entrenadores(request):
    entrenadores = Entrenador.objects.prefetch_related("pokemones").all()
    return render(
        request,
        "pokemon/lista_entrenadores.html",
        {"entrenadores": entrenadores},
    )


from .models import Gimnasio


def lista_gimnasios(request):
    gimnasios = Gimnasio.objects.select_related("lider").prefetch_related(
        "entrenadores_ganadores"
    )
    return render(
        request,
        "pokemon/lista_gimnasios.html",
        {"gimnasios": gimnasios},
    )

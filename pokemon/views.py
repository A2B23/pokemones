from django.shortcuts import render
from .models import Pokemon
from .forms import PokemonForm
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404



def lista_pokemones(request):
    pokemones = Pokemon.objects.all()
    return render(
        request,
        "pokemon/lista_pokemones.html",
        {"pokemones": pokemones},
    )


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
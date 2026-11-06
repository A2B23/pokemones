from django.urls import path
from . import views

app_name = "pokemon"

urlpatterns = [
    path("", views.lista_pokemones, name="lista"),
    path("pokemon/crear/", views.crear_pokemon, name="crear"),
    path("pokemon/<int:pk>/editar/", views.editar_pokemon, name="editar"),
    path("pokemon/<int:pk>/eliminar/",views.eliminar_pokemon,name="eliminar",),
    path("entrenadores/", views.lista_entrenadores, name="entrenadores"),
    path("gimnasios/", views.lista_gimnasios, name="gimnasios"),
    path("quiz/", views.quiz_pokemon, name="quiz"),
    path("api/quiz/pregunta/", views.api_pregunta_quiz, name="api_pregunta_quiz"),
]

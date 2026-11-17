from django.db import models
from django.conf import settings


class Pokemon(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    peso = models.DecimalField(max_digits=6, decimal_places=2)
    imagen = models.URLField(blank=True)
    entrenador = models.ManyToManyField(
        "Entrenador",
        blank=True,
        related_name="pokemones",
    )
    habilidades = models.CharField(max_length=200, blank=True)
    elemento = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Gimnasio(models.Model):
    lider = models.ForeignKey(
        "Entrenador",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gimnasios_liderados",
    )
    elemento = models.CharField(max_length=50)
    medallas = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Gimnasio de {self.elemento}"


class Entrenador(models.Model):
    documento = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    medallas = models.ManyToManyField(
        Gimnasio,
        blank=True,
        related_name="entrenadores_ganadores",
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Perfil(models.Model):
    class Rol(models.TextChoices):
        ENTRENADOR = "entrenador", "Entrenador"
        JUGADOR = "jugador", "Jugador"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_pokemon",
    )
    rol = models.CharField(max_length=20, choices=Rol.choices)
    entrenador = models.OneToOneField(
        Entrenador,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="perfil_usuario",
    )

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"

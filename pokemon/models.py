from django.db import models


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
from django.db import models

class Dueno(models.Model):
    nombre     = models.CharField(max_length=100)
    telefono   = models.CharField(max_length=20)
    email      = models.EmailField(unique=True)
    direccion  = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Mascota(models.Model):
    ESPECIES = [('perro','Perro'),('gato','Gato'),('ave','Ave'),('otro','Otro')]
    nombre   = models.CharField(max_length=100)
    especie  = models.CharField(max_length=10, choices=ESPECIES)
    raza     = models.CharField(max_length=100, blank=True)
    edad     = models.PositiveIntegerField()
    dueno    = models.ForeignKey(Dueno, on_delete=models.CASCADE, related_name='mascotas')

    def __str__(self):
        return f'{self.nombre} ({self.especie})'

class Consulta(models.Model):
    mascota     = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='consultas')
    fecha       = models.DateField()
    diagnostico = models.TextField()
    costo       = models.DecimalField(max_digits=10, decimal_places=2)
    veterinario = models.CharField(max_length=100)

    def __str__(self):
        return f'Consulta {self.id} – {self.mascota.nombre}'
# Create your models here.

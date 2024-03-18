from django.db import models

class Noticia(models.Model):
    urlimagen = models.URLField(max_length=200)
    enlace = models.URLField(max_length=200)
    titular = models.CharField(max_length=150)
    autores = models.CharField(max_length=100)
    contenido = models.TextField()
    fextraccion = models.DateTimeField()
    publicada = models.BooleanField(default=False)

    def __str__(self):
        if hasattr(self, 'fuente'):  # Revisar si hay fuentes asociadas
            # Iterar sobre las fuentes relacionadas y obtener el nombre de cada una
            fuentes = ", ".join([fuente.nfuente for fuente in self.fuente.all()])
            return "{} - {}".format(self.titular, fuentes)
        else:
            return self.titular

class Fuente(models.Model):
    nfuente = models.CharField(max_length=50)
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='fuente')

    def __str__(self):
        return self.nfuente
from django.db import models



class InfoActe(models.Model):
    numero_assure = models.CharField(max_length=255, null=True)
    medecin = models.CharField(max_length=255, null=True)
    acte = models.IntegerField(null=True)
    affection = models.CharField(max_length=100, null=True)
    rc = models.CharField(max_length=255, null=True)

    def __str__(self):
        pass

    class Meta:
        managed = False

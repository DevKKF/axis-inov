
from import_export import resources

from configurations.models import Acte, Affection, Prestataire


class ActeResource(resources.ModelResource):
    class Meta:
        model = Acte
        fields = ('name',)
        exclude = ('id',)
        
class AffectionResource(resources.ModelResource):
    class Meta:
        model = Affection
        fields = ('name',)
        exclude = ('id',)   
        
class PrestataireResource(resources.ModelResource):
    class Meta:
        model = Prestataire
        fields = ('name',)
        exclude = ('id',) 
        
class RubriqueResource(resources.ModelResource):
    class Meta:
        model = Prestataire
        fields = ('name',)
        exclude = ('id',)                     
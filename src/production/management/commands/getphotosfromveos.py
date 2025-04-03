import base64
import string

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from production.models import Carte, Aliment
from shared.helpers import generer_qrcode_carte
from shared.veos import get_aliment_id_adoc, get_document


class Command(BaseCommand):
    help = 'Récupérer les photos des VEOS'

    def add_arguments(self, parser):
        parser.add_argument("--numero_carte", type=str, help="Numéro de carte de l'assuré")
        parser.add_argument("--nombre", type=int, help="Nombre de bénéficiaires pour lesquels on récupère les photos")

    def handle(self, *args, **options):
        numero_carte = options['numero_carte']
        nombre = options['nombre'] if options['nombre'] else 10000

        if numero_carte:
            aliments = Aliment.objects.filter(veos_numero_carte=numero_carte, has_photo_veos=True, statut_import_photo_veos=False)[:1]
        else:
            # execution de la requête pour récupérer les aliments sans photo du niger
            aliments = Aliment.objects.filter(veos_numero_carte__isnull=False, photo="", bureau_id=54, has_photo_veos=True, statut_import_photo_veos=False)[:nombre]
            if not aliments:
                aliments = Aliment.objects.filter(veos_numero_carte__isnull=False, photo="", has_photo_veos=True, statut_import_photo_veos=False)[:nombre]

        for aliment in aliments:
            try:
                numero_carte_active = aliment.veos_numero_carte
                veos_id_aliment = numero_carte_active[:-1]
                ID_ADOC = get_aliment_id_adoc(veos_id_aliment)

                # Appel de la fonction pour effectuer l'appel à l'API
                api_response = get_document(ID_ADOC)

                if 'datas' in api_response:
                    base64_img = api_response['datas']

                    # Remove the prefix 'data:image/jpeg;base64,' from the base64 string
                    img_data = base64_img.split(';base64,')[-1]

                    # Decode base64 to binary data
                    binary_data = base64.b64decode(img_data)

                    # Create ContentFile object from binary data
                    content_file = ContentFile(binary_data, name='photo.jpg')  # Adjust name as needed

                    # Assign content file to the photo field of the Aliment instance
                    photo_name = f'photo_{veos_id_aliment}.jpg'

                    aliment.photo.save(photo_name, content_file, save=True)

                    # indiquer que la photo a été importée
                    aliment.statut_import_photo_veos = True

                    # mettre à jour le statut importation de la photo
                    aliment.save()

                    self.stdout.write(self.style.SUCCESS(f'Récupération de photos effectuée pour {numero_carte_active}'))


                else:
                    aliment.has_photo_veos = False
                    # mettre à jour le statut importation de la photo
                    aliment.save()

                    self.stdout.write(self.style.SUCCESS(f'Photo non trouvé pour {numero_carte_active}'))

            except Exception as e:
                # En cas d'erreur, marquer l'aliment comme non traité et continuer
                aliment.has_photo_veos = False
                aliment.observation = f'{aliment.observation}, : UploadPhotoError: {str(e)}'
                aliment.save()

                self.stdout.write(self.style.ERROR(f'Erreur lors de la récupération de la photo pour {aliment.veos_code_aliment}: {str(e)}'))


        self.stdout.write(self.style.SUCCESS('Récupération de photos effectuée avec succès'))
import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from configurations.helper_config import send_dev_notification_background_task_mail
from configurations.models import AlimentBaobab
from production.models import Carte, Aliment, AlimentFormule, Police
from shared.enum import StatutValidite, Statut
from shared.helpers import generer_qrcode_carte


class Command(BaseCommand):
    help = "Execution de script pour actualiser l'etat des bénéficiaires d'une police"

    def add_arguments(self, parser):
        parser.add_argument("--numero_police", type=str, help="Numéro de police")

    def handle(self, *args, **options):
        #try:
        numero_police = options['numero_police']
        police = Police.objects.filter(numero=numero_police).first()
        today = datetime.datetime.now(tz=timezone.utc)

        if police:
            aliment_ids = AlimentFormule.objects.filter(
                formule_id__in=[p.id for p in police.formules],
                statut=Statut.ACTIF,
                statut_validite=StatutValidite.VALIDE
            ).values_list('aliment_id', flat=True)

            queryset = Aliment.objects.filter(id__in=aliment_ids).order_by('adherent_principal_id',
                                                                           'qualite_beneficiaire_id', 'nom',
                                                                           'prenoms')

            # print(str(queryset.query))

            data = []
            liste_aliments_ajoutes = []

            for aliment in queryset:
                if aliment.id not in liste_aliments_ajoutes:
                    liste_aliments_ajoutes.append(aliment.id)

                historique_formules = aliment.historique_formules.filter(formule__police=police).exclude(
                    statut_validite=StatutValidite.SUPPRIME).order_by('date_debut')

                date_entree_police = historique_formules.first().date_debut if historique_formules else None

                numero_carte = aliment.carte_active().numero if aliment.carte_active() else None
                derniere_formule = AlimentFormule.objects.filter(aliment=aliment).order_by('-id').first()
                derniere_formule_libelle = derniere_formule.formule.libelle if derniere_formule and derniere_formule.formule else ''
                etat_beneficiaire = aliment.etat_beneficiaire_atdate(today)
                sa_formule = aliment.formule_atdate(today)
                sa_formule_libelle = sa_formule.libelle if sa_formule else ''

                #aliment.date_entree_police=
                #aliment.formule=derniere_formule_libelle
                aliment.etat = etat_beneficiaire
                aliment.save()


            self.stdout.write(self.style.SUCCESS(f'Aliment updated '))

        #except Exception as e:
        #    self.stdout.write(self.style.FAILURE(str(e)))


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from shared.enum import DesignationRemboursementSinistre, StatutRemboursementSinistre
from sinistre.helper_sinistre import get_retenue_selon_contexte
from sinistre.models import RemboursementSinistre, Sinistre

 
class Command(BaseCommand):
    help = 'Execution de mise à jour des retenues des sinistre notamment AIB pour le benin'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Commande exécutée !'))
        try:
            sinistres = Sinistre.objects.filter(prestataire__bureau__code="BN01", dossier_sinistre_id__isnull=False)
            nombre_update_new = 0
            nombre_update = 0
            for sinistre in sinistres:
                self.stdout.write(self.style.SUCCESS(f'Mise à jour du sinistre N°' + str(sinistre.numero)))

                if sinistre.taux_retenue is None or sinistre.taux_retenue==0:
                    sinistre.taux_retenue = get_retenue_selon_contexte(sinistre.prestataire.id)
                    sinistre.save()
                    nombre_update_new += 1
                rb_sinistre_ACCEPTE = RemboursementSinistre.objects.filter(sinistre=sinistre, statut=StatutRemboursementSinistre.ACCEPTE, is_invalid=False).first()
                rb_sinistre_TXT = RemboursementSinistre.objects.filter(sinistre=sinistre, statut=StatutRemboursementSinistre.TAXT, is_invalid=False).first()
                if sinistre.taux_retenue is not None and rb_sinistre_ACCEPTE is not None and rb_sinistre_TXT is None and sinistre.facture_prestataire.type_remboursement.code == "TP":
                    montant_tps = int((int(sinistre.montant_remb_accepte)*sinistre.taux_retenue)/100)
                    RemboursementSinistre.objects.create(designation=DesignationRemboursementSinistre.TAXT,
                                                        sinistre=sinistre,
                                                        montant=montant_tps,
                                                        motif="ajustement AIB Bénin",
                                                        statut=StatutRemboursementSinistre.TAXT)
                    sinistre.tps = montant_tps
                    sinistre.save()
                    nombre_update += 1  
                if sinistre.taux_retenue is not None and rb_sinistre_ACCEPTE is not None and rb_sinistre_TXT is not None and (sinistre.tps is None or sinistre.tps == 0) and sinistre.facture_prestataire.type_remboursement.code == "TP":
                    sinistre.tps = rb_sinistre_TXT.montant
                    sinistre.save()
                    nombre_update += 1  
            self.stdout.write(self.style.SUCCESS(f'Sinistre(s) {nombre_update} modifié(s) ({nombre_update_new} nouveau(x)) / {sinistres.count()} parcouru(s) avec succès !'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))

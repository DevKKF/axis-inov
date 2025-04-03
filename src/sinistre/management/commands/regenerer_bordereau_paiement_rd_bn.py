from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from configurations.models import Compagnie
from shared.enum import DesignationRemboursementSinistre, StatutRemboursementSinistre, StatutValidite
from sinistre.helper_sinistre import get_retenue_selon_contexte
from sinistre.models import PaiementComptable, RemboursementSinistre, Sinistre
from shared.helpers import generate_random_string, render_pdf
from django.core.files import File

 
class Command(BaseCommand):
    help = 'Execution de mise à jour des retenues des sinistre notamment AIB pour le benin'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Commande exécutée !'))
        
        sinistres_concernes_ids = Sinistre.objects.filter(prestataire__bureau__code="BN01", dossier_sinistre_id__isnull=False, dossier_sinistre__type_remboursement__code="RD", observation='Retrait taux retenue sur les RD').values_list('bordereau_ordonnancement_id', flat=True)
        paiement_comptables_concernees = PaiementComptable.objects.filter(bordereau_ordonnancement_id__in=sinistres_concernes_ids)
        
        nombre_update = 0
        
        for paiement_comptable in paiement_comptables_concernees:
            self.stdout.write(self.style.SUCCESS(f'Mise à jour du BORDEREAU DE PAIEMENT COMPTABLE de N°' + str(paiement_comptable.numero)))
            try:
            
                # Fetch the PaiementComptable instance
                #paiement_comptable = get_object_or_404(PaiementComptable, id=paiement_comptable_id)

                # Retrieve the associated BordereauOrdonnancement
                bordereau = paiement_comptable.bordereau_ordonnancement

                # Retrieve all sinistres associated with the bordereau
                liste_sinistres = Sinistre.objects.filter(bordereau_ordonnancement=bordereau, statut_validite=StatutValidite.VALIDE)

                # Get unique compagnies concerned by the sinistres
                liste_garant_concernes_ids = liste_sinistres.values_list('compagnie', flat=True).distinct()
                liste_garant_concernes = Compagnie.objects.filter(id__in=liste_garant_concernes_ids)

                sinistres_par_garants = []
                total_global_net_a_payer = Decimal(0)  # Initialize total net to pay

                for garant in liste_garant_concernes:
                    sinistres_compagnie_x = liste_sinistres.filter(compagnie=garant.id)

                    # Calculate totals for the current compagnie
                    total_frais_reel = sum((sinistre.frais_reel or 0) for sinistre in sinistres_compagnie_x)
                    total_part_benef = sum((sinistre.part_assure or 0) for sinistre in sinistres_compagnie_x)
                    total_base_remb = sum((Decimal(sinistre.total_frais_reel) if sinistre.tm_prefinanced else Decimal(sinistre.total_part_compagnie) or 0) for sinistre in sinistres_compagnie_x)
                    total_rejete = sum((sinistre.montant_remb_refuse or 0) for sinistre in sinistres_compagnie_x)
                    total_base_taxable = sum((sinistre.montant_remb_accepte or 0) for sinistre in sinistres_compagnie_x)
                    total_taxe_tbs = sum((sinistre.montant_taxe_tbs or 0) for sinistre in sinistres_compagnie_x)
                    total_taxe_far = sum((sinistre.montant_taxe_far or 0) for sinistre in sinistres_compagnie_x)
                    total_taxes = total_taxe_tbs + total_taxe_far
                    total_net_a_payer = total_base_taxable + total_taxes

                    # Update the global total
                    total_global_net_a_payer += total_net_a_payer

                    garant_x = {
                        'name': garant,
                        'sinistres': sinistres_compagnie_x,
                        'nbre_total_sinistres': len(sinistres_compagnie_x),
                        'total_frais_reel': total_frais_reel,
                        'total_part_benef': total_part_benef,
                        'total_base_remb': total_base_remb,
                        'total_rejete': total_rejete,
                        'total_base_taxable': total_base_taxable,
                        'total_taxes': total_taxes,
                        'total_taxe_tbs': total_taxe_tbs,
                        'total_taxe_far': total_taxe_far,
                        'total_net_a_payer': total_net_a_payer,
                    }
                    sinistres_par_garants.append(garant_x)

                # Update the Montant total in the PaiementComptable instance
                paiement_comptable.montant_total = total_global_net_a_payer
                paiement_comptable.observation = "Retrait AIB sur les RD"
                paiement_comptable.save()
                nombre_update += 1

                total_global_nombre_sinistres = sum(r['nbre_total_sinistres'] for r in sinistres_par_garants)
                total_global_part_assure = sum(r['total_part_benef'] for r in sinistres_par_garants)
                total_global_frais_reel = sum(r['total_frais_reel'] for r in sinistres_par_garants)
                total_global_rejete = sum(r['total_rejete'] for r in sinistres_par_garants)
                total_global_base_remboursement = sum(r['total_base_remb'] for r in sinistres_par_garants)
                total_global_base_taxable = sum(r['total_base_taxable'] for r in sinistres_par_garants)
                total_global_taxe_tbs = sum(r['total_taxe_tbs'] for r in sinistres_par_garants)
                total_global_taxe_far = sum(r['total_taxe_far'] for r in sinistres_par_garants)
                total_global_taxes = total_global_taxe_far + total_global_taxe_tbs
                # total_global_net_a_payer = sum(r['total_net_a_payer'] for r in sinistres_par_garants)
                
                # Generate the PDF
                pdf = render_pdf("pdf/bordereau_reglement_garant.html", context_dict={
                    'sinistres_par_garants': sinistres_par_garants,
                    'bordereau': bordereau,
                    'paiement_comptable': paiement_comptable,
                    'total_global_net_a_payer': total_global_net_a_payer,
                    'total_global_nombre_sinistres': total_global_nombre_sinistres,
                    'total_global_part_assure': total_global_part_assure,
                    'total_global_frais_reel': total_global_frais_reel,
                    'total_global_rejete': total_global_rejete,
                    'total_global_base_remboursement': total_global_base_remboursement,
                    'total_global_base_taxable': total_global_base_taxable,
                    'total_global_taxe_tbs': total_global_taxe_tbs,
                    'total_global_taxe_far': total_global_taxe_far,
                    'total_global_taxes': total_global_taxes,
                })
 
                # Save the regenerated PDF in the PaiementComptable model
                paiement_comptable.fichier.save(f'bordereau_paiement_comptable_{paiement_comptable.numero}.pdf', File(pdf))
                paiement_comptable.save()
                self.stdout.write(self.style.SUCCESS(f'Borderau(x) Paiement(s) {nombre_update} modifié(s) / {paiement_comptables_concernees.count()} parcouru(s) avec succès !'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
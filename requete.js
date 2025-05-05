$(document).ready(function () {

    function chargerInfosCompagnieProduit() {
        let compagnie_id = $("#modal-modification_police #compagnie_modification").val();
        let produit_id = $('#modal-modification_police #produit_modification').val();

        // Réinitialiser les champs
        $('#modal-modification_police #taux_com_courtage_modification').val('');
        $('#modal-modification_police #taux_com_courtage_terme_modification').val('');
        $('#modal-modification_police #taux_com_gestion').val('');

        if (compagnie_id && produit_id) {
            $.ajax({
                type: 'get',
                url: '/production/compagnie/ajax_infos_compagnie_modification/' + compagnie_id + '/' + produit_id,
                dataType: 'json',
                success: function (data) {
                    let taux_com_courtage = parseFloat(data.taux_com_courtage);
                    let taux_com_courtage_terme = parseFloat(data.taux_com_courtage_terme);

                    console.log('taux_com_courtage : ', taux_com_courtage);
                    console.log('taux_com_courtage_terme : ', taux_com_courtage_terme);

                    $('#modal-modification_police #taux_com_courtage_modification').val(taux_com_courtage);
                    $('#modal-modification_police #taux_com_courtage_terme_modification').val(taux_com_courtage_terme);

                    calculer_montant_divers_police_modification();
                },
                error: function () {
                    console.log('Erreur de chargement : ajax_infos_compagnie_modification ');
                }
            });
        }
    }

    $("#modal-modification_police #compagnie_modification, #modal-modification_police #produit_modification").on('change', function () {
        chargerInfosCompagnieProduit();
    });

    $(document).on("keyup change", "#modal-modification_police .calculs_handler_police_modification", function (event) {
        if (event.which == 13) {
            event.preventDefault();
        }
        calculer_montant_divers_police_modification();
    });

    function calculer_montant_divers_police_modification() {
        let prime_ht = parseInt($('#modal-modification_police #prime_ht_modification').val().replaceAll(' ', ''));
        let cout_police_compagnie = parseInt($('#modal-modification_police #cout_police_compagnie_modification').val().replaceAll(' ', ''));
        let cout_police_courtier = parseInt($('#modal-modification_police #cout_police_courtier_modification').val().replaceAll(' ', ''));
        let taxe = parseInt($('#modal-modification_police #taxe_modification').val().replaceAll(' ', ''));
        let autres_taxes = parseInt($('#modal-modification_police #autres_taxes_modification').val().replaceAll(' ', ''));

        let taux_com_gestion = parseFloat($('#modal-modification_police #taux_com_gestion').val());
        let taux_com_courtage = parseFloat($('#modal-modification_police #taux_com_courtage_modification').val());
        let taux_com_courtage_terme = parseFloat($('#modal-modification_police #taux_com_courtage_terme_modification').val());

        if (isNaN(prime_ht)) { prime_ht = 0; }
        if (isNaN(cout_police_compagnie)) { cout_police_compagnie = 0; }
        if (isNaN(cout_police_courtier)) { cout_police_courtier = 0; }
        if (isNaN(taxe)) { taxe = 0; }
        if (isNaN(autres_taxes)) { autres_taxes = 0; }
        if (isNaN(taux_com_gestion)) { taux_com_gestion = 0; }
        if (isNaN(taux_com_courtage)) { taux_com_courtage = 0; }

        let prime_ttc = prime_ht + cout_police_compagnie + cout_police_courtier + taxe + autres_taxes;

        console.log('prime_ht_modification : ', prime_ht);
        console.log('cout_police_compagnie_modification : ', cout_police_compagnie);
        console.log('cout_police_courtier_modification : ', cout_police_courtier);
        console.log('taxe_modification : ', taxe);
        console.log('autres_taxes_modification : ', autres_taxes);
        console.log('taux_com_gestion_modification : ', taux_com_gestion);
        console.log('taux_com_courtage_modification : ', taux_com_courtage);
        console.log('prime_ttc_modification : ', prime_ttc);

        let montant_commission_gestion = (taux_com_gestion / 100) * prime_ht;
        let montant_commission_courtage = (taux_com_courtage / 100) * prime_ht;

        let total_taux_com_affaire_nouvelle = 0;
        let total_taux_com_renouvelement = 0;
        let montant_commission_intermediaire = 0;
        let total_montant_commission_intermediaire = 0;

        $('.taux_com_affaire_nouvelle_modification').each(function () {
            let taux_com_affaire_nouvelle = parseFloat($(this).val());
            let taux_com_renouvelement = parseFloat($(this).closest('tr').find('.taux_com_renouvelement_modification').val());
            let base_calcul_taux_retrocession = $(this).closest('tr').find('.base_calcul_taux_retrocession_modification').val();
            let intermediaire = $(this).closest('tr').find('.intermediaire_modification').val();

            if (intermediaire != "" && base_calcul_taux_retrocession != "" && taux_com_affaire_nouvelle > 0) {
                if (base_calcul_taux_retrocession == 1) {//sur prime ht
                    montant_commission_intermediaire = (taux_com_affaire_nouvelle / 100) * prime_ht;
                } else if (base_calcul_taux_retrocession == 2) {//sur com courtage
                    montant_commission_intermediaire = (taux_com_affaire_nouvelle / 100) * montant_commission_courtage;
                } else if (base_calcul_taux_retrocession == 3) {//sur com gestion
                    montant_commission_intermediaire = (taux_com_affaire_nouvelle / 100) * montant_commission_gestion;
                } else if (base_calcul_taux_retrocession == 4) {//sur com total (courtage + gestion)
                    montant_commission_intermediaire = (taux_com_affaire_nouvelle / 100) * (montant_commission_courtage + montant_commission_gestion);
                }
                console.log(montant_commission_intermediaire);
                total_montant_commission_intermediaire = total_montant_commission_intermediaire + montant_commission_intermediaire;
                console.log(total_montant_commission_intermediaire);
            }
        });

        $('#modal-modification_police #prime_ttc_modification').val(prime_ttc);
        $('#modal-modification_police #commission_courtage_modification').val(montant_commission_courtage);
        $('#modal-modification_police #commission_gestion_modification').val(montant_commission_gestion);
        $('#modal-modification_police #total_commission_intermediaire_modification').val(total_montant_commission_intermediaire);
    }

    $('#modal-modification_police').on('shown.bs.modal', function () {
        chargerInfosCompagnieProduit(); // Appeler la fonction au chargement du modal
    });

});
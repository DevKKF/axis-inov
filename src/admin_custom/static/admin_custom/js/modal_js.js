
$(document).ready(function () {
    //TODO DEBUT RECUPERATION DES MOTIFS VIA LE MODAL AVENANT
    // Écouteur pour le changement de motif
    $('#motif').on('change', function () {
        let motif_id = $(this).val();

        // Sélectionner tous les champs à l'intérieur des blocs
        let fieldsGeneralToModify = $('#modal-modification_police #general_modification').find('input, select, textarea');
        let fieldsIntermediaireToModify = $('#modal-modification_police #intermediaire_modification').find('input, select, textarea');
        let fieldsGarantieToModify = $('#modal-modification_police #garantie_modification').find('input, select, textarea');
        let fieldsRisqueToModify = $('#modal-modification_police #risque_modification').find('input, select, textarea');
        let fieldsAlimentToModify = $('#modal-modification_police #aliment_modification').find('input, select, textarea, button');
        let fieldsVehiculeToModify = $('#modal-modification_police #vehicule_modification').find('input, select, textarea');
        let fieldsMarchandiseToModify = $('#modal-modification_police #marchandise_modification').find('input, select, textarea');
        let fieldsFacturationToModify = $('#modal-modification_police #facturation_modification').find('input, select, textarea');
        let fieldsPrimeToModify = $('#modal-modification_police #prime_modification').find('input, select, textarea');

        // Fonction pour désactiver les champs
        function disableFields(fields) {
            fields.each(function() {
                if ($(this).is('select')) {
                    // Pour les <select>, désactiver et ajouter un champ caché
                    $(this).prop('disabled', true);
                    $(this).after(`<input type="hidden" name="${$(this).attr('name')}" value="${$(this).val()}">`);
                } else if ($(this).is('input[type="radio"], input[type="checkbox"]')) {
                    // Pour les boutons radio et cases à cocher, désactiver et empêcher les clics
                    $(this).prop('disabled', true);
                    $(this).on('click', function(e) {
                        e.preventDefault();
                    });
                } else {
                    // Pour les autres champs, utiliser readonly
                    $(this).prop('readonly', true);
                }
            });
        }

        // Fonction pour réactiver les champs
        function enableFields(fields) {
            fields.each(function() {
                if ($(this).is('select')) {
                    // Pour les <select>, réactiver et supprimer le champ caché
                    $(this).prop('disabled', false);
                    $(this).next('input[type="hidden"]').remove();
                } else if ($(this).is('input[type="radio"], input[type="checkbox"]')) {
                    // Pour les boutons radio et cases à cocher, réactiver
                    $(this).prop('disabled', false);
                    $(this).off('click');
                } else {
                    // Pour les autres champs, désactiver readonly
                    $(this).prop('readonly', false);
                }
            });
        }

        // Changement de garantie
        if (motif_id == 5) {
            disableFields(fieldsGeneralToModify);
            disableFields(fieldsIntermediaireToModify);
            disableFields(fieldsRisqueToModify);
            disableFields(fieldsAlimentToModify);
            disableFields(fieldsVehiculeToModify);
            disableFields(fieldsMarchandiseToModify);
            disableFields(fieldsFacturationToModify);
            disableFields(fieldsPrimeToModify);
        }
        // Incorporation
        if (motif_id == 10) {
            disableFields(fieldsGeneralToModify);
            disableFields(fieldsIntermediaireToModify);
            disableFields(fieldsGarantieToModify);
            disableFields(fieldsRisqueToModify);
            disableFields(fieldsVehiculeToModify);
            disableFields(fieldsMarchandiseToModify);
            disableFields(fieldsFacturationToModify);
            disableFields(fieldsPrimeToModify);
        }
        // Retrait
        if (motif_id == 12) {
            disableFields(fieldsGeneralToModify);
            disableFields(fieldsIntermediaireToModify);
            disableFields(fieldsGarantieToModify);
            disableFields(fieldsRisqueToModify);
            disableFields(fieldsVehiculeToModify);
            disableFields(fieldsMarchandiseToModify);
            disableFields(fieldsFacturationToModify);
            disableFields(fieldsPrimeToModify);
        }
        else {
            // Réactiver tous les champs si le motif n'est pas 5, 10 ou 12
        }
    });

    // Using jQuery
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie != '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    // Déclencher manuellement l'événement 'change' au chargement de la page
    $('#motif').trigger('change');

    //TODO FIN RECUPERATION DES MOTIFS VIA LE MODAL AVENANT

    //TODO DEBUT DU CALCUL DES TAUX ET DES PRIMES DE LA MARCHANDISE
    $(document).on("keyup change", "#modal-modification_police .calculs_marchandise_montant_police_modification", function (event) {
        if (event.which == 13) {
            event.preventDefault();
        }
        calculer_montant_marchandise_modification();
    });

    function calculer_montant_marchandise_modification() {
        let valeur_assuree = parseInt($('#modal-modification_police #valeur_assuree_modification').val().replaceAll(' ', ''));

        // Si la valeur assurée est vide ou égale à 0, vider tous les autres champs
        if (isNaN(valeur_assuree) || valeur_assuree === 0) {
            $('#modal-modification_police #taux_risque_ordinaire_modification').val('');
            $('#modal-modification_police #taux_risque_guerre_modification').val('');
            $('#modal-modification_police #taux_supprime_modification').val('');
            $('#modal-modification_police #taux_reduction_commerciale_modification').val('');
            $('#modal-modification_police #taux_taxe_modification').val('');
            $('#modal-modification_police #accessoires_modification').val('');
            $('#modal-modification_police #autres_frais_modification').val('');
            $('#modal-modification_police #prime_risque_ordinaire_modification').val('');
            $('#modal-modification_police #prime_risque_guerre_modification').val('');
            $('#modal-modification_police #prime_supprime_modification').val('');
            $('#modal-modification_police #prime_brut_modification').val('');
            $('#modal-modification_police #prime_reduction_modification').val('');
            $('#modal-modification_police #total_taxe_modification').val('');
            $('#modal-modification_police #prime_ttc_mar_modification').val('');
            return; // Arrêter l'exécution de la fonction
        }

        let taux_risque_ordinaire = parseInt($('#modal-modification_police #taux_risque_ordinaire_modification').val().replaceAll(' ', ''));
        let taux_risque_guerre = parseInt($('#modal-modification_police #taux_risque_guerre_modification').val().replaceAll(' ', ''));
        let taux_supprime = parseInt($('#modal-modification_police #taux_supprime_modification').val().replaceAll(' ', ''));
        let taux_reduction_commerciale = parseInt($('#modal-modification_police #taux_reduction_commerciale_modification').val().replaceAll(' ', ''));
        let taux_taxe = parseInt($('#modal-modification_police #taux_taxe_modification').val().replaceAll(' ', ''));
        let accessoires = parseInt($('#modal-modification_police #accessoires_modification').val().replaceAll(' ', ''));
        let autres_frais = parseInt($('#modal-modification_police #autres_frais_modification').val().replaceAll(' ', ''));

        if (isNaN(taux_risque_ordinaire)) { taux_risque_ordinaire = 0; }
        if (isNaN(taux_risque_guerre)) { taux_risque_guerre = 0; }
        if (isNaN(taux_supprime)) { taux_supprime = 0; }
        if (isNaN(taux_reduction_commerciale)) { taux_reduction_commerciale = 0; }
        if (isNaN(taux_taxe)) { taux_taxe = 0; }
        if (isNaN(accessoires)) { accessoires = 0; }
        if (isNaN(autres_frais)) { autres_frais = 0; }

        // Calcul des valeurs saisies
        let prime_risque_ordinaire = (taux_risque_ordinaire / 100) * valeur_assuree;
        let prime_risque_guerre = (taux_risque_guerre / 100) * valeur_assuree;
        let prime_supprime = (taux_supprime / 100) * valeur_assuree;
        let prime_brut = prime_risque_ordinaire + prime_risque_guerre + prime_supprime;
        let prime_reduction = (taux_reduction_commerciale / 100) * prime_brut;
        let total_taxe = (taux_taxe / 100) * prime_brut;
        let prime_ttc_mar = (prime_brut - prime_reduction) + total_taxe + accessoires + autres_frais;

        console.log('valeur_assuree', valeur_assuree);
        console.log('taux_risque_ordinaire', taux_risque_ordinaire);
        console.log('prime_risque_ordinaire', prime_risque_ordinaire);
        console.log('taux_risque_guerre', taux_risque_guerre);
        console.log('prime_risque_guerre', prime_risque_guerre);
        console.log('prime_supprime', prime_supprime);
        console.log('prime_risque_guerre', prime_risque_guerre);
        console.log('prime_brut', prime_brut);
        console.log('taux_reduction_commerciale', taux_reduction_commerciale);
        console.log('prime_reduction', prime_reduction);
        console.log('total_taxe', total_taxe);
        console.log('accessoires', accessoires);
        console.log('autres_frais', autres_frais);
        console.log('prime_ttc_mar', prime_ttc_mar);

        $('#modal-modification_police #prime_risque_ordinaire_modification').val(prime_risque_ordinaire);
        $('#modal-modification_police #prime_risque_guerre_modification').val(prime_risque_guerre);
        $('#modal-modification_police #prime_supprime_modification').val(prime_supprime);
        $('#modal-modification_police #prime_brut_modification').val(prime_brut);
        $('#modal-modification_police #prime_reduction_modification').val(prime_reduction);
        $('#modal-modification_police #total_taxe_modification').val(total_taxe);
        $('#modal-modification_police #prime_ttc_mar_modification').val(prime_ttc_mar);
    }
    //TODO FIN DU CALCUL DES TAUX ET DES PRIMES DE LA MARCHANDISE
});


//TODO validation / Téléchargement de fichier / suppression session
$(document).ready(function() {

    function isValidDate(dateStr) {
        return dateStr && !isNaN(Date.parse(dateStr));
    }

    function manageModeRenouvellement() {
        let modeRenouvellement = $('#modification_mode_renouvellement').val();
        let dateDebutPoliceInput = $('#modification_date_debut_effet');
        let dateFinPoliceInput = $('#modification_date_fin_police');
        let dateFinPoliceLabelStar = $('#modification_label_date_fin_police .required');
        let fractionnementSelect = $('select[name="fractionnement"]');
        let fractionnement_hint = $('#modification_fractionnement_hint');

        // 1. Réinitialiser champ "Date fin contrat"
        dateFinPoliceInput.removeAttr('required');
        dateFinPoliceLabelStar.hide();

        // 2. Réinitialiser champ "Fractionnement"
        fractionnementSelect.val(''); // vide la sélection
        fractionnementSelect.prop('disabled', false); // réactive le champ

        // 3. Si mode = Temporaire → forcer "Échéance unique" et désactiver
        if (modeRenouvellement === "Temporaire") {
            dateDebutPoliceInput.removeAttr('required');
            dateFinPoliceInput.attr('required', 'required');
            dateFinPoliceLabelStar.show();
            fractionnement_hint.show();

            // Trouver et sélectionner "Échéance unique"
            let optionUnique = fractionnementSelect.find('option').filter(function () {
                return $(this).text().trim() === "Echéance unique";
            });

            if (optionUnique.length) {
                fractionnementSelect.val(optionUnique.val());
                fractionnementSelect.prop('disabled', true);
            }
        }
        else {
            dateFinPoliceLabelStar.hide();
            dateDebutPoliceInput.removeAttr('required');
            dateFinPoliceInput.removeAttr('required');
            fractionnement_hint.hide();

            // Réactiver et vider le champ "Fractionnement"
            fractionnementSelect.prop('disabled', false);
            fractionnementSelect.val('');

            // Cacher "Échéance unique" dans les autres cas
            fractionnementSelect.find('option').filter(function () {
                return $(this).text().trim() === "Echéance unique";
            }).hide();
        }
    }

    function validateDates() {
        let dateDebut = $('#modification_date_debut_effet').val();
        let dateFinEffet = $('#modification_date_fin_effet').val();
        let dateFinPolice = $('#modification_date_fin_police').val();
        let mode = $('#modification_mode_renouvellement').val();
        let btnSubmit = $('#btn_save_modification_police');

        btnSubmit.removeAttr('disabled');

        if (isValidDate(dateDebut)) {
            if (mode === "Tacite Reconduction" && isValidDate(dateFinEffet)) {
                if (new Date(dateDebut) >= new Date(dateFinEffet)) {
                    notifyWarning("La date de renouvellement doit être strictement postérieure à la date de début.");
                    btnSubmit.attr('disabled', 'disabled');
                    return false;
                }
            } else if ((mode === "Sans Tacite Reconduction" || mode === "Temporaire") && isValidDate(dateFinPolice)) {
                if (new Date(dateDebut) >= new Date(dateFinPolice)) {
                    notifyWarning("La date de fin du contrat doit être strictement postérieure à la date de début.");
                    btnSubmit.attr('disabled', 'disabled');
                    return false;
                }
            }
        }

        return true;
    }

    // Initialisation
    $(document).ready(function () {
        manageModeRenouvellement();
        validateDates();
    });

    // Sur changement
    $(document).on('change', "#modification_mode_renouvellement, #modification_date_fin_effet, #modification_date_fin_police", function () {
        manageModeRenouvellement();
        validateDates();
    });

    // Pour le téléchargement du fichier modèle de création d'aliment
    $('#telecharger_modele_modification').on('click', function () {
        // Récupérer le chemin du fichier depuis l'attribut "download-modification-fichier"
        const filePath = $(this).attr('download-modification-fichier');

        // Vérifier l'existence du fichier via une requête fetch
        fetch(filePath, { method: 'HEAD' }).then(response => {
            if (response.ok) {
                // Si le fichier existe, déclencher le téléchargement
                const link = document.createElement('a');
                link.href = filePath;
                link.download = filePath.split('/').pop();
                link.click();
            } else {
                // Si le fichier n'existe pas, afficher un message d'erreur
                alert('Le fichier demandé est introuvable.');
            }
        })
        .catch(error => {
            // Gérer les erreurs réseau ou autres
            console.error('Erreur lors de la vérification du fichier:', error);
            alert('Une erreur est survenue. Veuillez réessayer plus tard.');
        });
    });

    // Lorsque le modal est complètement fermé
    $('#modal-modification_police').on('hidden.bs.modal', function () {
        $.ajax({
            url: '/production/clear_session/',
            type: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (response) {
                if (response.success) {
                    console.log(response.message);
                } else {
                    console.error(response.error || 'Erreur lors de la suppression de la session.');
                }
            },
            error: function () {
                console.error('Erreur de communication avec le serveur.');
            }
        });
    });
});


$(document).ready(function () {

    // Fonction pour formater un montant en séparateurs de milliers
    function formatThousands(value) {
        if (!value) return '';
        return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    // Fonction pour gérer l'affichage du bloc en fonction de la réponse à "Garantie"
    function handleGarantieChange() {
        let garantieValue = $('input[name="garantie"]:checked').val();
        let policeId = $("#police_id").val();
        $('.aliment_obligatoire_modification').removeAttr('required');

        if (garantieValue === "NON") {
                $('#formule_block_modification').hide();
            $('#test_garantie_modification').hide();
            $("#table_garantie_police_modification tbody").empty();
        } else {
            $('#formule_block_modification').show();
            $('#test_garantie_modification').show();
            $('.aliment_obligatoire_modification').attr('required', true);

            // Charger les garanties uniquement si "OUI" est sélectionné
            if (policeId) {
                loadGarantiesPolice(policeId);
            }
        }
    }

    // Écouteur d'événement pour les changements de réponse à "Garantie"
    $('input[name="garantie"]').on('change', function () {
        handleGarantieChange();

    });

    // Appliquer les règles au chargement de la page
    handleGarantieChange();

    // Fonction pour charger les garanties d'une police au chargement du modal
    function loadGarantiesPolice(policeId) {
        $("#table_garantie_police_modification tbody").empty();
        $('#garantie-message-success').text('').hide();
        $('#garantie-message-warning').text('').hide();
        $('#garantie-message-danger').text('').hide();

        $.ajax({
            url: "/production/get_garanties_by_police/",
            type: "GET",
            data: { police_id: policeId },
            success: function (data) {
                populateGarantiesTable(data.garanties);
            },
            error: function () {
                $("#garantie-message-danger").text("Erreur lors du chargement des garanties.").show().delay(5000).fadeOut();
            }
        });
    }

    // Fonction pour charger les garanties selon la formule sélectionnée
    function loadGarantiesFormule(formuleId, policeId) {
        $("#table_garantie_police_modification tbody").empty();
        $('#garantie-message-success').text('').hide();
        $('#garantie-message-warning').text('').hide();
        $('#garantie-message-danger').text('').hide();

        $.ajax({
            url: "/production/get_garanties_by_formule_modification/",
            type: "GET",
            data: { formule_id: formuleId, police_id: policeId },
            success: function (data) {
                populateGarantiesTable(data.garanties);
            },
            error: function () {
                $("#garantie-message-danger").text("Erreur lors du chargement des garanties.").show().delay(5000).fadeOut();
            }
        });
    }

    // Remplir le tableau des garanties
    function populateGarantiesTable(garanties) {
        if (garanties.length === 0) {
            $("#garantie-message-warning").text("Aucune garantie trouvée.").show().delay(5000).fadeOut();
        }

        garanties.forEach((garantie, index) => {
            let row = `
                <tr>
                    <td style="vertical-align:middle;">
                        <input type="checkbox" class="form-control garantie-checkbox" name="garantie_${garantie.id}" value="${garantie.id}" style="width: 1rem; height: 1.25rem;" ${garantie.active ? 'checked' : ''}>
                    </td>
                    <td style="vertical-align:middle;">${garantie.nom}</td>
                    <td style="vertical-align:middle;padding:5px;">
                        <input type="text" class="form-control form-control-sm franchise-input money_field" name="franchise_${garantie.id}" value="${garantie.franchise}" onkeypress="isInputNumber(event)" oninput="formatMontant(this)" ${garantie.active ? '' : 'disabled'}>
                    </td>
                    <td style="vertical-align:middle;padding:5px;">
                        <input type="text" class="form-control form-control-sm capital-input money_field" name="capital_${garantie.id}" value="${garantie.capital}" onkeypress="isInputNumber(event)" oninput="formatMontant(this)" ${garantie.active ? '' : 'disabled'}>
                    </td>
                </tr>
            `;
            $("#table_garantie_police_modification tbody").append(row);
        });
    }

    // Chargement des garanties au changement de la formule
    $("#formule_modification").change(function () {
        let formuleId = $(this).val();
        let policeId = $("#police_id").val();
        let garantieValue = $('input[name="garantie"]:checked').val();

        // Vérifier si "OUI" est sélectionné avant de charger les garanties
        if (garantieValue === "OUI" && formuleId) {
            loadGarantiesFormule(formuleId, policeId);
        }
    });

    // Chargement des garanties dès l'ouverture du modal, si "OUI" est sélectionné
    $("#modal-modification_police").on("show.bs.modal", function () {
        let policeId = $("#police_id").val();
        let garantieValue = $('input[name="garantie"]:checked').val();

        if (garantieValue === "OUI" && policeId) {
            loadGarantiesPolice(policeId);
        }

    });

    $(document).on('change', '.aliment-checkbox', function () {
        const parentRow = $(this).closest('tr');
        const DateSortieInput = parentRow.find('.datesortie-input');

        if ($(this).is(':checked')) {
            DateSortieInput.prop('disabled', false);
        } else {
            DateSortieInput.prop('disabled', true).val('');
        }
    });

    // Fonction pour gérer l'affichage du bloc en fonction de la réponse à "Apporteur"
    function handleApporteurChange() {
        let apporteurValue = $('input[name="apporteur"]:checked').val();

        if (apporteurValue === "NON") {
            $('#test_modification').hide();
        } else {
            $('#test_modification').show();
        }
    }

    // Écouteur d'événement pour les changements de réponse à "Apporteur"
    $('input[name="apporteur"]').on('change', function () {
        handleApporteurChange();
    });

    // Fonction pour gérer l'affichage du bloc en fonction de la réponse à "Participation"
    function handleParticipationChange() {
        let participationValue = $('input[name="participation"]:checked').val();

        if (participationValue === "NON") {
            $('#box_taux_participation_modification').hide();
        } else {
            $('#box_taux_participation_modification').show();
        }
    }

    // Écouteur d'événement pour les changements de réponse à "Participation"
    $('input[name="participation"]').on('change', function () {
        handleParticipationChange();

    });

    // Appliquer les règles au chargement de la page
    handleApporteurChange();
    handleParticipationChange();

    // Masquer les champs au chargement de la page
    $('.box_typecompagnie_modification').hide();
    $('#box_compagnie_modification').hide();

    // Fonction pour gérer les changements de compagnie
    function handleCompagnieChange() {
        let compagnieId = $('#compagnie_modification').val();

        // Si une compagnie est sélectionnée, afficher le champ "Autre assureur"
        if (compagnieId) {
            $('.box_typecompagnie_modification').show();
        } else {
            $('.box_typecompagnie_modification').hide();
            $('#box_compagnie_modification').hide(); // Masquer le champ suivant si la compagnie est désélectionnée
        }
    }

    // Fonction pour gérer les changements de type de compagnie
    function handleTypeCompagnieChange() {
        let typeCompagnieId = $('#typecompagnie_modification').val();

        // Si un type de compagnie est sélectionné (autre que "Aucun"), afficher le champ "Choisir l'assureur"
        if (typeCompagnieId) {
            $('#box_compagnie_modification').show();
        } else {
            $('#box_compagnie_modification').hide(); // Masquer le champ si "Aucun" est sélectionné
        }
    }

    // Écouteur d'événement pour les changements de compagnie
    $('#compagnie_modification').on('change', function () {
        handleCompagnieChange();
    });

    // Écouteur d'événement pour les changements de type de compagnie
    $('#typecompagnie_modification').on('change', function () {
        handleTypeCompagnieChange();
    });

    // Appliquer les règles au chargement de la page
    handleCompagnieChange();
    handleTypeCompagnieChange();
});



//
$(document).ready(function () {
    // Fonction pour récupérer le CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const modalModificationPolice = $('#modal-modification_police');
    const brancheModification = $('#branche_modification');
    const produitModification = $('#produit_modification');
    const produitModifId = $('#produit_modif_id');
    const compagnieModification = $('#compagnie_modification');
    const policeIdModification = $('#police_id');

    const ongletRisqueTab = $('[href="#risque"]');
    const ongletMarchandiseTab = $('[href="#marchandise"]');
    const ongletAlimentTab = $('[href="#aliment"]');
    const ongletVehiculeTab = $('[href="#vehicule"]');

    const ongletRisqueContent = $('.risque');
    const ongletMarchandiseContent = $('.marchandise');
    const ongletAlimentContent = $('.aliment');
    const ongletVehiculeContent = $('.vehicule');

    // Variable pour stocker l'ID du produit courant
    let currentProduitId = produitModifId.val();

    // Function to show/hide relevant onglets and manage tab activation
    function toggleOnglets(produitCode) {
        // Hide all content divs
        ongletRisqueContent.hide();
        ongletMarchandiseContent.hide();
        ongletAlimentContent.hide();
        ongletVehiculeContent.hide();

        // Deactivate all tabs
        ongletRisqueTab.removeClass('active');
        ongletMarchandiseTab.removeClass('active');
        ongletAlimentTab.removeClass('active');
        ongletVehiculeTab.removeClass('active');

        if (produitCode == 10001) { // Mono-Véhicule
            ongletVehiculeContent.show();
            ongletVehiculeTab.addClass('active');
        }
        else if (produitCode == 10002) { // Flotte-Auto
            ongletAlimentContent.show();
            ongletAlimentTab.addClass('active');
        }
         else if (produitCode == 50001 || produitCode === 50002) { // Marchandise
            ongletMarchandiseContent.show();
            ongletMarchandiseTab.addClass('active');
        }
        else { // Risque
            ongletRisqueContent.show();
            ongletRisqueTab.addClass('active');
        }
    }

    // Lorsque la fenêtre modale est affichée, déclenchez l'événement « change » sur la liste déroulante de la branche.
    modalModificationPolice.on('shown.bs.modal', function () {
        brancheModification.trigger('change');

        const policeId = policeIdModification.val();
        chargerAlimentsDepuisSession(policeId);

    });

    // Gérer l'événement de changement pour la liste déroulante « branche ».
    brancheModification.on('change', function () {
        const brancheIdModification = $(this).val();
        const produitModifIdVal = produitModifId.val();

        // Reset the produit dropdown
        produitModification.html('<option value="">Choisir un produit</option>');

        // Initially
        toggleOnglets(null);

        $.ajax({
            type: 'get',
            url: `/production/ajax_produits/${brancheIdModification}`,
            dataType: 'json',
            success: function (produits) {
                let produitSelectionneParDefaut = false;

                produits.forEach(function (produit) {
                    const option = $('<option>', {
                        value: produit.pk,
                        text: produit.fields.nom
                    });

                    if (produit.pk == produitModifIdVal) {
                        option.prop('selected', true);
                        produitSelectionneParDefaut = true;
                        toggleOnglets(produit.fields.code); // Show relevant onglet based on pre-selected product

                        // Mettre à jour l'ID du produit actuel
                        currentProduitId = produit.pk;
                    }

                    produitModification.append(option);
                });

                // Trigger 'change' on produit dropdown if a default product was selected
                if (produitSelectionneParDefaut) {
                    produitModification.trigger('change');

                    // Déclencher ensuite le changement de compagnie après la sélection du produit
                    setTimeout(function() {
                        compagnieModification.trigger('change');
                    }, 100);
                }
            },
            error: function () {
                console.error('Erreur lors du chargement des produits pour la modification.');
            }
        });
    });

    // Gérer l'événement de changement pour la liste déroulante « produit » dans la fenêtre modale
    produitModification.on('change', function () {
        const produitIdModification = $(this).val();

        // Si un produit est sélectionné, mettre à jour l'ID du produit actuel
        if (produitIdModification) {
            currentProduitId = produitIdModification;
            console.log('Produit changé, nouvelle valeur:', currentProduitId);
        }

        toggleOnglets(produitIdModification ? $(this).find('option:selected').data('code') : null);

        if (produitIdModification) {
            $.ajax({
                type: 'get',
                url: `/production/produit/${produitIdModification}/sous-menu`,
                success: function (produit) {
                    if (produit && produit.length > 0) {
                        produitModification.find('option:selected').data('code', produit[0].fields.code);
                        toggleOnglets(produit[0].fields.code);
                    } else {
                        toggleOnglets(null);
                        console.warn('Aucun détail de produit trouvé.');
                    }
                },
                error: function () {
                    console.error('Erreur lors du chargement des détails du produit pour la modification.');
                }
            });
        } else {
            toggleOnglets(null);
        }
    });

    // Gérer l'événement de chargement des aliments liés à la police
    function afficherAlimentsDansTableau(data) {
        const tbody = $("#table_liste_aliment_modification tbody");
        tbody.empty(); // Vider l'ancien contenu
        data.forEach((row, index) => {
            tbody.append(`
                <tr data-index="${index}">
                    <td>
                        <button class="btn btn-danger btn-sm btn-supprimer-aliment" data-index="${index}">
                            <i class="fa fa-remove"></i>
                        </button>
                    </td>
                    <td>${row.immat || ''}</td>
                    <td>${row.marque || ''}</td>
                    <td>${row.modele || ''}</td>
                    <td>${row.T_categorie_id || ''}</td>
                    <td>${row.date_entree || ''}</td>
                    <td>${row.proprietaire || ''}</td>
                    <td>${row.conducteur || ''}</td>
                </tr>
            `);
        });
    }

    function chargerAlimentsDepuisSession(policeId) {
        console.log('Chargement des aliments pour la police ID:', policeId);
        $.ajax({
            url: "/production/get_aliments_session/",
            type: "GET",
            data: { police_id: policeId },
            success: function (response) {
                if (response.success) {
                    afficherAlimentsDansTableau(response.data);
                } else {
                    console.log("Aucun aliment en session.");
                }
            },
            error: function () {
                console.error("Erreur lors du chargement des aliments.");
            }
        });
    }


    // Gérer l'événement de changement de police
    $('#ChargementAlimentPolice').on('change', function () {
        const policeId = $(this).val();

        $.ajax({
            url: "/production/get_aliments_session/",
            type: "GET",
            data: { police_id: policeId },
            success: function (response) {
                if (response.success) {
                    afficherAlimentsDansTableau(response.data);
                } else {
                    console.log("Aucun aliment en session.");
                }
            },
            error: function () {
                console.error("Erreur lors du chargement des aliments.");
            }
        });
    });

    // Suppression d’un aliment (déléguée)
    $(document).on('click', '.btn-supprimer-aliment', function () {
        const index = $(this).data('index');
        $.ajax({
            url: `/production/supprimer_aliment/${index}/`,
            type: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            success: function (response) {
                if (response.success) {
                    $(`tr[data-index="${index}"]`).remove();
                } else {
                    console.error(response.error || 'Erreur lors de la suppression.');
                }
            },
            error: function () {
                console.error('Erreur de communication avec le serveur.');
            }
        });
    });

    // Soumission du formulaire manuel
    $('#btn_save_police_aliment').on('click', function () {
        $('.mod_aliment_champ_obligatoire').removeClass('is-invalid is-valid');
        $('#message-modal-error, #message-modal-warning, #message-modal-success').hide();

        let valide = true;
        $('.mod_aliment_champ_obligatoire').each(function () {
            const value = $(this).val().trim();
            if (!value) {
                $(this).addClass('is-invalid');
                valide = false;
            } else {
                $(this).addClass('is-valid');
            }
        });

        if (!valide) {
            $('#message-modal-error').text('Veuillez remplir tous les champs obligatoires.').show().delay(5000).fadeOut();
            return;
        }

        const formData = new FormData($('#form_add_police_aliment')[0]);

        $.ajax({
            url: '/production/import-formulaire-aliments/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success) {
                    $('#message-modal-success').text(response.message).show().delay(5000).fadeOut();
                    afficherAlimentsDansTableau(response.data);
                    $("#form_add_police_aliment").trigger("reset");
                    $(".mod_aliment_champ_obligatoire").removeClass('is-valid is-invalid');
                    $("#form_add_police_aliment select").prop('selectedIndex', 0).trigger('change');
                } else {
                    $('#message-modal-warning').text(response.message).show().delay(5000).fadeOut();
                }
            },
            error: function (xhr) {
                const response = xhr.responseJSON;
                if (xhr.status === 500) {
                    $("#message-modal-error").text(response?.message || "Erreur serveur").show().delay(5000).fadeOut();
                } else if (xhr.status === 400) {
                    $("#message-modal-warning").text(response?.message || "Erreur dans les données").show().delay(5000).fadeOut();
                } else {
                    $("#message-modal-error").text(response?.message || "Erreur inattendue").show().delay(5000).fadeOut();
                }
            }
        });
    });

    // Importation via fichier Excel
    $("#importation_aliment").on("click", function () {
        const inputFichier = $("#fichier_aliment");
        const fichier = inputFichier.prop("files")[0];

        if (!fichier) {
            inputFichier.css("border-color", "red");
            $("#message-warning").text("Veuillez sélectionner un fichier.").show().delay(5000).fadeOut();
            return;
        }

        inputFichier.css("border-color", "");
        const formData = new FormData();
        formData.append("fichier_aliment", fichier);

        $.ajax({
            url: "/production/import-excel-aliments/",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            success: function (response) {
                if (response.success) {
                    $("#message-success").text(response.message).show().delay(5000).fadeOut();
                    afficherAlimentsDansTableau(response.data);
                    $("#fichier_aliment").val('').removeClass('is-valid is-invalid');
                } else {
                    $("#message-warning").text(response.message).show().delay(5000).fadeOut();
                }
            },
            error: function (xhr) {
                const response = xhr.responseJSON;
                if (xhr.status === 500) {
                    $("#message-error").text(response?.message || "Erreur serveur").show().delay(5000).fadeOut();
                } else if (xhr.status === 400) {
                    $("#message-warning").text(response?.message || "Erreur dans les données").show().delay(5000).fadeOut();
                } else {
                    $("#message-error").text(response?.message || "Erreur inattendue").show().delay(5000).fadeOut();
                }
            }
        });
    });

    // Gérer l'événement de changement de compagnie dans le modal de modification
    $(document).on("keyup change", "#modal-modification_police .calculs_handler_police_modification", function (event) {
         if (event.which == 13) {
             event.preventDefault();
         }
         console.log('Événement keyup ou change détecté sur:', this); // Ajout pour le débogage
         calculer_montant_divers_police();
     });

    function calculer_montant_divers_police() {
         let prime_ht = parseFloat($('#modal-modification_police #prime_ht').val().replaceAll(' ', '')) || 0;
         let cout_police_compagnie = parseFloat($('#modal-modification_police #cout_police_compagnie').val().replaceAll(' ', '')) || 0;
         let cout_police_courtier = parseFloat($('#modal-modification_police #cout_police_courtier').val().replaceAll(' ', '')) || 0;
         let taxe = parseFloat($('#modal-modification_police #taxe').val().replaceAll(' ', '')) || 0;
         let autres_taxes = parseFloat($('#modal-modification_police #autres_taxes').val().replaceAll(' ', '')) || 0;
         let taux_com_gestion = parseFloat($('#modal-modification_police #taux_com_gestion').val()) || 0;
         let taux_com_courtage = parseFloat($('#modal-modification_police #taux_com_courtage').val()) || 0;
         let taux_com_courtage_terme = parseFloat($('#modal-modification_police #taux_com_courtage_terme').val()) || 0;

         let prime_ttc = prime_ht + cout_police_compagnie + cout_police_courtier + taxe + autres_taxes;
         let montant_commission_gestion = (taux_com_gestion / 100) * prime_ht;
         let montant_commission_courtage = (taux_com_courtage / 100) * prime_ht;
         let total_montant_commission_intermediaire = 0;

         console.log('prime_ht (dans la fonction)', prime_ht); // Ajout pour le débogage
         console.log('cout_police_compagnie', cout_police_compagnie);
         console.log('cout_police_courtier', cout_police_courtier);
         console.log('taxe', taxe);
         console.log('autres_taxes', autres_taxes);
         console.log('taux_com_gestion', taux_com_gestion);
         console.log('taux_com_courtage', taux_com_courtage);
         console.log('taux_com_courtage_terme', taux_com_courtage_terme);
         console.log('prime_ttc (avant affichage)', prime_ttc);

         $('.taux_com_affaire_nouvelle').each(function () {
             let taux_com_affaire_nouvelle = parseFloat($(this).closest('tr').find('.taux_com_affaire_nouvelle').val());
             let taux_com_renouvelement = parseFloat($(this).closest('tr').find('.taux_com_renouvelement').val());
             let base_calcul_taux_retrocession = $(this).closest('tr').find('.base_calcul_taux_retrocession').val();
             let intermediaire = $(this).closest('tr').find('.intermediaire').val();
             let montant_commission_intermediaire = 0;

             console.log('-------------------------------');
             console.log('taux_com_affaire_nouvelle', taux_com_affaire_nouvelle);
             console.log('taux_com_renouvelement', taux_com_renouvelement);
             console.log('base_calcul_taux_retrocession', base_calcul_taux_retrocession);
             console.log('intermediaire', intermediaire);
             console.log('-------------------------------');

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
                 console.log('montant_commission_intermediaire', montant_commission_intermediaire);
                 total_montant_commission_intermediaire += montant_commission_intermediaire;
                 console.log('total_montant_commission_intermediaire', total_montant_commission_intermediaire);
             }
         });

         $('#modal-modification_police #prime_ttc').val(prime_ttc);
         $('#modal-modification_police #commission_courtage').val(montant_commission_courtage);
         $('#modal-modification_police #commission_gestion').val(montant_commission_gestion);
         $('#modal-modification_police #total_commission_intermediaire').val(total_montant_commission_intermediaire);
    }

    function reloadInfosCompagnieProduit() {
         const compagnieIdModification = compagnieModification.val();
         const produitIdModification = currentProduitId || produitModification.val() || produitModifId.val();

         // Réinitialiser les champs spécifiques aux taux de commission
         modalModificationPolice.find('#taux_com_courtage').val('');
         modalModificationPolice.find('#taux_com_courtage_terme').val('');
         modalModificationPolice.find('#taux_com_gestion').val(''); // Ajout de la réinitialisation du taux de gestion

         if (compagnieIdModification && produitIdModification) {
             $.ajax({
                 type: 'get',
                 url: '/production/compagnie/ajax_infos_compagnie/' + compagnieIdModification + '/' + produitIdModification,
                 dataType: 'json',
                 success: function (data) {
                     let taux_com_courtage = parseFloat(data.taux_com_courtage) || 0;
                     let taux_com_courtage_terme = parseFloat(data.taux_com_courtage_terme) || 0;
                     let taux_com_gestion = parseFloat(data.taux_com_gestion) || 0; // Récupération du taux de gestion

                     modalModificationPolice.find('#taux_com_courtage').val(taux_com_courtage);
                     modalModificationPolice.find('#taux_com_courtage_terme').val(taux_com_courtage_terme);
                     modalModificationPolice.find('#taux_com_gestion').val(taux_com_gestion); // Affichage du taux de gestion

                     calculer_montant_divers_police(); // Appel de la fonction de calcul après la récupération des infos
                 },
                 error: function () {
                     console.log('Erreur de chargement : ajax_infos_compagnie');
                 }
             });
         }
    }

     // Lorsqu'on change la compagnie
    compagnieModification.on('change', function () {
         reloadInfosCompagnieProduit();
    });

     // Si tu veux déclencher aussi via le changement de produit, tu peux appeler aussi :
    produitModification.on('change', function () {
         reloadInfosCompagnieProduit();
    });

});


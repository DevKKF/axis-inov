//TODO RECUPERATION DES MOTIFS VIA LE MODAL AVENANT
$(document).ready(function () {
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

        // Autres champs à griser
        $('.aliment_bloc_global').hide();
        $('.aliment_bloc_retrait').hide();

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
            $('.aliment_bloc_global').show();
            $('.aliment_bloc_retrait').hide();
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
            $('.aliment_bloc_global').show();
            $('.aliment_bloc_retrait').hide();
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
            $('.aliment_bloc_global').hide();
            $('.aliment_bloc_retrait').show();
        }
        else {
            $('.aliment_bloc_global').show();
            $('.aliment_bloc_retrait').hide();
        }
    });

    // Déclencher manuellement l'événement 'change' au chargement de la page
    $('#motif').trigger('change');

    $("#importation_aliment_modification").on("click", function () {
        const inputFichier = $("#fichier_aliment_modification");
        const fichier = inputFichier.prop("files")[0];

        if (!fichier) {
            inputFichier.css("border-color", "red");
            $("#message-warning").text("Veuillez sélectionner un fichier.").delay(5000).fadeOut();
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
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            success: function (response) {
                if (response.success) {
                    // Réinitialiser tous les champs du formulaire
                    $("#fichier_aliment_modification").trigger("reset");
                    $("#message-success").text(response.message).show().delay(5000).fadeOut();
                    console.log(response.data);
                    // Mettre à jour le tableau avec les nouvelles données
                    const tbody = $("#table_liste_aliment_modification tbody");
                    response.data.forEach((row, index) => {
                        tbody.append(`
                            <tr data-immat="${row.immat}">
                                <td>
                                    <button type="button" class="btn btn-danger btn-sm delete-btn">
                                        <i class="fa fa-trash-o"></i>
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

                    $('#fichier_aliment_modification').removeClass('is-valid').removeClass('is-invalid');

                } else {
                    $("#message-warning").text(response.message).delay(5000).fadeOut();
                }
            },
            error: function (xhr) {
                // Gérer les erreurs 500 ou autres erreurs inattendues
                const response = xhr.responseJSON;
                if (xhr.status === 500) {
                    $("#message-error").text(response?.message || "Une erreur interne du serveur est survenue. Veuillez réessayer plus tard.").show().delay(5000).fadeOut();
                } else if (xhr.status === 400) {
                    $("#message-warning").text(response?.message || "Erreur dans les données soumises. Veuillez vérifier votre fichier.").show().delay(5000).fadeOut();
                } else {
                    $("#message-error").text(response?.message || "Une erreur inattendue est survenue. Veuillez réessayer.").show().delay(5000).fadeOut();
                }
            },
        });
    });

    $('#btn_save_modification_police_aliment_modification').on('click', function () {
        // Supprimer les erreurs précédentes
        $('.mod_aliment_champ_obligatoire').removeClass('is-invalid').removeClass('is-valid');
        $('#message-modal-error').text('').hide();
        $('#message-modal-warning').text('').hide();
        $('#message-modal-success').text('').hide();

        // Valider les champs obligatoires
        let valide = true;
        $('.mod_aliment_champ_obligatoire').each(function () {
            let value = $(this).val().trim();
            // Validation spécifique pour les <select>
            if ($(this).is('select')) {
                if (!value || value === "") {
                    $(this).addClass('is-invalid'); // Ajouter classe invalide
                    valide = false;
                } else {
                    $(this).removeClass('is-invalid').addClass('is-valid'); // Ajouter classe valide
                }
            } else {
                // Validation pour les autres types de champs
                if (!value) {
                    $(this).addClass('is-invalid'); // Ajouter classe invalide
                    valide = false;
                } else {
                    $(this).removeClass('is-invalid').addClass('is-valid'); // Ajouter classe valide
                }
            }
        });

        if (!valide) {
            // Afficher un message si un champ obligatoire est vide
            $('#message-modal-error').text('Veuillez remplir tous les champs obligatoires.').show();
            setTimeout(() => $('#message-modal-error').fadeOut(), 5000);
            return;
        }

        // Récupérer les données du formulaire
        const formData = new FormData($('#form_add_police_aliment_modification')[0]);

        // Requête Ajax pour envoyer les données au backend
        $.ajax({
            url: '/production/import-formulaire-aliments/',
            type: 'POST',
            data: formData,
            processData: false, // Indique que nous envoyons un FormData
            contentType: false, // Pour ne pas encoder les données
            success: function (response) {
                if (response.success) {
                    // Afficher le message de succès
                    $("#message-modal-success").text(response.message).show().delay(5000).fadeOut();

                    // Mettre à jour le tableau avec les nouvelles données
                    const tbody = $("#table_liste_aliment_modification tbody");
                    response.data.forEach((row, index) => {
                        tbody.append(`
                            <tr data-immat="${row.immat}">
                                <td>
                                    <button type="button" class="btn btn-danger btn-sm delete-btn">
                                        <i class="fa fa-trash-o"></i>
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

                    // Réinitialiser tous les champs du formulaire
                    $("#form_add_police_aliment_modification").trigger("reset");
                    $("#form_add_police_aliment_modification select").each(function() {
                        $(this).prop('selectedIndex', 0).trigger('change');
                    });
                    $('.mod_aliment_champ_obligatoire').removeClass('is-valid').removeClass('is-invalid');

                } else {
                    // Afficher un message d'avertissement
                    $("#message-modal-warning").text(response.message).show().delay(5000).fadeOut();
                }
            },
            error: function (xhr) {
                // Gérer les erreurs 500 ou autres erreurs inattendues
                const response = xhr.responseJSON;
                if (xhr.status === 500) {
                    $("#message-modal-error").text(response?.message || "Une erreur interne du serveur est survenue. Veuillez réessayer plus tard.").show().delay(5000).fadeOut();
                } else if (xhr.status === 400) {
                    $("#message-modal-warning").text(response?.message || "Erreur dans les données soumises. Veuillez vérifier votre fichier.").show().delay(5000).fadeOut();
                } else {
                    $("#message-modal-error").text(response?.message || "Une erreur inattendue est survenue. Veuillez réessayer.").show().delay(5000).fadeOut();
                }
            },
        });
    });

    // Écouter le clic sur le bouton de suppression
    $(document).on('click', '.delete-btn', function () {
        const immat = $(this).closest('tr').data('immat');

        // Effectuer la requête AJAX pour supprimer l'immatriculation
        $.ajax({
            url: '/production/supprimer_aliment_modification/',
            type: 'POST',
            data: { immat: immat },
            success: function (response) {
                if (response.success) {
                    // Si la suppression est réussie côté serveur, retirer la ligne du DOM
                    $(`tr[data-immat="${immat}"]`).remove();
                } else {
                    alert('Erreur lors de la suppression.');
                }
            },
            error: function () {
                alert('Erreur lors de la requête.');
            }
        });
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

    function ajouterAlimentsDansTableau(data) {
        const tbody = $("#table_liste_aliment_modification tbody");
        tbody.empty();
        data.forEach((row) => {
            tbody.append(`
                <tr data-immat="${row.immat}">
                    <td>
                        <button type="button" class="btn btn-danger btn-sm delete-btn">
                            <i class="fa fa-trash-o"></i>
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

    function chargerAlimentsSession() {
        let police_id = $('#police_id').val();
        $.ajax({
            url: "/production/get_aliments_session/",
            type: "GET",
            data: { police_id: police_id },
            success: function (response) {
                if (response.success) {
                    ajouterAlimentsDansTableau(response.data);
                } else {
                    console.warn("Aucun aliment en session.");
                }
            },
            error: function () {
                console.error("Erreur lors du chargement des aliments en session.");
            }
        });
    }

    // Lors du clic sur l'onglet "ALIMENTS"
    $("#aliment-tab_modification").on("click", function () {
        chargerAlimentsSession();
    });
});


//TODO validation / Téléchargement de fichier / suppression session
$(document).ready(function() {

    function isValidDate(dateStr) {
        return dateStr && !isNaN(Date.parse(dateStr));
    }

    function manage_mode_renouvellement() {
        let mode_renouvellement = $('#mode_renouvellement').val();

        // Cacher tous les champs et enlever les attributs required
        $('.tacide_reconduction, .sans_tacide_reconduction').hide();
        $('.tacide_reconduction input, .sans_tacide_reconduction input').removeAttr('required');

        if (mode_renouvellement === "Tacite Reconduction") {
            $('.tacide_reconduction').show();
            $('.tacide_reconduction input').attr('required', 'required');
        } else if (mode_renouvellement === "Sans Tacite Reconduction") {
            $('.sans_tacide_reconduction').show();
            $('.sans_tacide_reconduction input').attr('required', 'required');
        }
    }



    // Exécuter au chargement de la page
    $(document).ready(function () {
        manage_mode_renouvellement();
        validateDatesModification();
    });

    // Déclencher la gestion des modes et la validation des dates
    $(document).on('change', "#mode_renouvellement, #date_debut_effet, #date_fin_effet, #date_fin_police", function () {
        manage_mode_renouvellement();
        validateDatesModification();
    });

    // Gestion du bouton de modification avec validation des dates
    $(document).ready(function() {
        $("#btn_save_modification_police").on("click", function() {
            if (!validateDatesModification()) {
                return;
            }
        });
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

});


//TODO affichage sous-menu de la police
$(document).ready(function () {

    // Fonction utilitaire : Affiche un tab et rend les champs obligatoires
    function afficherOngletAvecChamps(tabSelector, champSelector) {
        $(tabSelector).removeClass('d-none');
        $(champSelector).attr('required', true);
    }

    // Liste des onglets dynamiques
    const ongletsDynamiques = ['#risque-tab_modification', '#aliment-tab_modification', '#vehicule-tab_modification', '#marchandise-tab_modification'];
    const champsDynamiques = ['.marchandise_champ_obligatoire_modification', '.vehicule_champ_obligatoire_modification'];

    // Liste des onglets fixes avec leurs champs obligatoires
    const ongletsFixes = [
        { tab: '#garantie-tab_modification', champ: '.garantie_champ_obligatoire' },
        { tab: '#general-tab_modification' },
        { tab: '#facturation-tab_modification' },
        { tab: '#prime-tab_modification' },
    ];

    // *** Initialisation ***
    // Masquer les onglets dynamiques
    $(ongletsDynamiques.join(', ')).addClass('d-none');
    $(champsDynamiques.join(', ')).removeAttr('required');
    $('#table_liste_aliment_modification tbody').empty();

    // Afficher les onglets fixes
    ongletsFixes.forEach(onglet => {
        $(onglet.tab).removeClass('d-none');
        if (onglet.champ) {
            $(onglet.champ).attr('required', true); // rendre les champs obligatoires
        }
    });


    // Fonction pour gérer les changements de produit
    function handleProduitChange(produit_id) {
        // Vérifier si un produit est sélectionné
        if (!produit_id) {
            // Si aucun produit sélectionné : masquer dynamiques, réinitialiser champs
            $(ongletsDynamiques.join(', ')).addClass('d-none');
            $(champsDynamiques.join(', ')).removeAttr('required');
            $('#table_liste_aliment tbody').empty();

            // Onglets fixes toujours visibles + champs required actifs
            ongletsFixes.forEach(onglet => {
                $(onglet.tab).removeClass('d-none');
                if (onglet.champ) {
                    $(onglet.champ).attr('required', true);
                }
            });

            return;
        }

        // Effectuer l'appel AJAX pour charger les sous-menus liés au produit sélectionné
        $.ajax({
            type: 'get',
            url: '/production/produit/' + produit_id + '/sous-menu',
            success: function (produit) {
                let produit_code = produit[0].fields.code;

                // Réinitialiser les dynamiques
                $(ongletsDynamiques.join(', ')).addClass('d-none');
                $(champsDynamiques.join(', ')).removeAttr('required');
                $('#table_liste_aliment_modification tbody').empty();

                // Réafficher les onglets fixes + champs required
                ongletsFixes.forEach(onglet => {
                    $(onglet.tab).removeClass('d-none');
                    if (onglet.champ) {
                        $(onglet.champ).attr('required', true);
                    }
                });

                // Logique produit_code : affichage dynamique
                if (produit_code == 10001) { // Mono-Véhicule
                    afficherOngletAvecChamps('#vehicule-tab_modification', '.vehicule_champ_obligatoire');
                } else if (produit_code == 10002) { // Flotte-Auto
                    afficherOngletAvecChamps('#aliment-tab_modification', '.mod_aliment_champ_obligatoire');
                } else if (produit_code == 50001 || produit_code == 50002) { // Produits marchandise
                    afficherOngletAvecChamps('#marchandise-tab_modification', '.marchandise_champ_obligatoire');
                } else {
                    afficherOngletAvecChamps('#risque-tab_modification');
                }

                // Déclenchement explicite du changement sur le produit pour mettre à jour les autres éléments
                $('#produit_modification').trigger('change');
            },
            error: function () {
                console.error('Erreur lors du chargement des sous-menus pour la modification.');
            }
        });
    }

    // Changement de produit dans le formulaire de modification
    $('#produit_modification').on('change', function () {
        let produit_id = $(this).val();
        handleProduitChange(produit_id);
    });

    // Détection automatique du produit actif dans le formulaire de modification au chargement
    let produit_id_initial = $('#produit_modification').val();
    if (produit_id_initial) {
        handleProduitChange(produit_id_initial);
    }

    // Gestion de l'ouverture du modal
    $('#modal-modification_police').on('shown.bs.modal', function () {
        let produit_id_initial = $('#produit_modification').val();
        if (produit_id_initial) {
            handleProduitChange(produit_id_initial);
        }
    });
});


//TODO Autres assureurs
$(document).ready(function () {
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
    handleCompagnieChange(); // Vérifier l'état initial de la compagnie
    handleTypeCompagnieChange(); // Vérifier l'état initial du type de compagnie
});


//TODO reponse Apporteur / Participant
$(document).ready(function () {
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
});


//TODO Garantie de la police
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
});



//TODO chargement des produits de la branche
$(document).ready(function () {
    function loadProduits(branche_id) {
        if (!branche_id) return; // Vérification pour éviter des appels inutiles

        $.ajax({
            type: 'GET',
            url: '/production/modification_ajax_produits/' + branche_id,
            dataType: 'json',
            success: function (produits) {
                let produitSelect = $('#produit_modification');
                produitSelect.empty().append('<option value="">Choisir un produit</option>');

                produits.forEach(function (produit) {
                    produitSelect.append('<option value="' + produit.pk + '">' + produit.fields.nom + '</option>');
                });

                let selectedProduitId = $('#police_produit_id').val();
                if (selectedProduitId) {
                    produitSelect.val(selectedProduitId);
                }
            },
            error: function () {
                console.error('Erreur lors du chargement des produits.');
            }
        });
    }

    // Récupération de la branche initialement sélectionnée et chargement des produits
    let initialBrancheId = $('#branche_modification').val();
    if (initialBrancheId) {
        loadProduits(initialBrancheId);
    }

    // Gestion du changement de branche
    $('#branche_modification').on('change', function () {
        let branche_id = $(this).val();
        loadProduits(branche_id);
    });
});


//TODO action sur les mouvements sur les sinistres
$(document).ready(function () {
    function getCSRFToken() {
        let csrfToken = null;
        const cookies = document.cookie.split(';');
        cookies.forEach(cookie => {
            const [key, value] = cookie.trim().split('=');
            if (key === 'csrftoken') {
                csrfToken = value;
            }
        });
        return csrfToken;
    }
    const csrf_token = getCSRFToken();

    // Changement des informations du vehicule
    $('#vehicule_id').on('change', function () {
        let vehicule_id = $(this).val();

        if (!vehicule_id) return;

        // Requête AJAX
        $.ajax({
            type: 'GET',
            url: '/production/police/information-vehicule/' + vehicule_id,
            success: function (vehicule) {
                if (vehicule.error) {
                    console.error('Erreur:', vehicule.error);
                    return;
                }

                // Remplissage du champ "risque"
                let immat_marque = vehicule.risque_info;
                $('#risque').val(immat_marque);

                // Vérification de la date de sortie
                let date_sortie = vehicule.date_sortie ? new Date(vehicule.date_sortie) : null;
                let date_actuelle = new Date();

                if (date_sortie && date_sortie < date_actuelle) {
                    //alert("Date sortie passé");
                    let n = noty({
                        text: 'Ce véhicule est déjà sortie. Voulez-vous continuer ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary',
                                text: 'Confirmer',
                                onClick: function ($noty) {
                                    $noty.close();
                                    $('#btn_save_modification_sinistre').prop('disabled', false);
                                }
                            },
                            {
                                addClass: 'btn btn-danger',
                                text: 'Annuler',
                                onClick: function ($noty) {
                                    $noty.close();
                                    $('#btn_save_modification_sinistre').prop('disabled', true);
                                }
                            }
                        ]
                    });
                } else {
                    $('#btn_save_modification_sinistre').prop('disabled', false);
                }
            },
            error: function () {
                console.error('Erreur lors du chargement des données.');
            }
        });
    });

    // Changement des informations de la marchandise
    $('#marchandise_id').on('change', function () {
        let marchandise_id = $(this).val();
        alert(marchandise_id);
        if (!marchandise_id) return;

        // Requête AJAX
        $.ajax({
            type: 'GET',
            url: '/production/police/information-marchandise/' + marchandise_id,
            success: function (marchandise) {
                if (marchandise.error) {
                    console.error('Erreur:', marchandise.error);
                    return;
                }

                // Remplissage du champ "risque"
                let immat_marchandise = marchandise.risque_info;
                $('#marchandise').val(immat_marchandise);
            },
            error: function () {
                console.error('Erreur lors du chargement des données.');
            }
        });
    });

    // Gestion de l'ouverture du modal
    $('#modal-modification_sinistre').on('shown.bs.modal', function () {
        let circonstanceId = $('#circonstance_id').val();
        let sinistreId = $('#sinistre_id').val();

        /**** Bloc du traitement des garanties et des provisions Début ****/

        //Récupérer les garanties du sinistre et de la circonstance
        if (circonstanceId !== '') {
            $.ajax({
                url: '/production/charger_garanties_circonstance_session_sinistre/',
                type: 'POST',
                headers: { "X-CSRFToken": getCSRFToken() },
                contentType: "application/json",
                data: JSON.stringify({
                    circonstance_id: circonstanceId,
                    sinistre_id: sinistreId
                }),
                success: function (response) {
                    if (response.success) {
                        afficherGarantiesSessionSinistre();
                    } else {
                        console.error("Aucune garantie chargée.");
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Erreur lors du chargement initial des garanties :", error);
                }
            });
        }

        $('#btn_ajout_garantie').click(function(event) {
            event.preventDefault();
            chargerGarantiesSinistre();
        });

        $('#circonstance_id').change(function() {
            viderGarantiesSessionSinistre();
            circonstanceId = $(this).val();
        });

        function chargerGarantiesSinistre() {
            var circonstanceId = $('#circonstance_id').val();

            if (circonstanceId === '') {
                let n = noty({
                    text: "Veuillez choisir une circonstance avant d'ajouter une garantie.",
                    type: 'warning',
                    dismissQueue: true,
                    layout: 'center',
                    theme: 'defaultTheme',
                    buttons: [
                        {
                            addClass: 'btn btn-primary',
                            text: 'Fermer',
                            onClick: function ($noty) {
                                $noty.close();
                            }
                        }
                    ]
                });
            } else {
                $("#circonstance_garantie_null").hide();
                $.ajax({
                    url: '/production/recuperer_garantie_circonstance_sinistre/',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        circonstance_id: circonstanceId,
                        sinistre_id: sinistreId
                    }),
                    success: function (response) {
                        if (response.status === 'no_garanties') {
                            let n = noty({
                                text: "Cette circonstance n'a aucune garantie affiliée.",
                                type: 'warning',
                                dismissQueue: true,
                                layout: 'center',
                                theme: 'defaultTheme',
                                buttons: [
                                    {
                                        addClass: 'btn btn-primary',
                                        text: 'Fermer',
                                        onClick: function ($noty) {
                                            $noty.close();
                                        }
                                    }
                                ]
                            });
                        } else {
                            $('#modal-sinistre_garantie').modal('show');
                            $("#circonstance_garantie_existe").html(response);
                            $("#circonstance_garantie_existe").show();
                            $("#table_add_sinistre_garantie").html(response);
                        }
                    },
                    error: function (xhr) {
                        console.error("Une erreur est survenue lors de la récupération des garanties.");
                    }
                });
            }
        }

        function viderGarantiesSessionSinistre() {
            $.ajax({
                url: '/production/vider_garanties_sinistre/',
                type: 'POST',
                success: function(response) {
                    if (response.success) {
                        afficherGarantiesSessionSinistre();
                    } else {
                        console.error("Erreur lors du vidage des garanties en session.");
                    }
                },
                error: function(xhr) {
                    console.error("Erreur lors du vidage des garanties en session.");
                }
            });
        }
        
        function afficherGarantiesSessionSinistre() {
            $.ajax({
                url: "/production/recuperer_garanties_circonstance_sinistre/",
                type: "GET",
                cache: false, // Désactiver le cache
                success: function (response) {
                    let table2 = $("#table_garantie_sinistre tbody");
                    table2.empty();

                    if (response.garanties && response.garanties.length > 0) {
                        // Garanties présentes, cacher garantie_null
                        $("#garantie_null").hide();

                        $.ajax({
                            url: "/production/afficher_provision_circonstance_sinistre/",
                            type: "GET",
                            data: {
                                sinistre_id: sinistreId
                            },
                            success: function (response) {
                                console.log(response);
                                $("#garantie_existe").show();
                                $("#garantie_existe").html(response);
                                $("#table_provision_sinistre_container").html(response);
                            },
                            error: function (xhr, status, error) {
                                console.error("Erreur lors du chargement du tableau des provisions :", error);
                            }
                        });

                        response.garanties.forEach(function (garantie) {
                            let row = `
                                <tr data-id="${garantie.id}">
                                    <td><span class="btn btn-danger btn-sm btn-delete-garantie" data-id="${garantie.id}"><i class="fa fa-trash-o"></i></span></td>
                                    <td>${garantie.nom}</td>
                                    <td class="text-center">${garantie.mouvement}</td>
                                    <td class="text-center">${garantie.date}</td>
                                </tr>
                            `;
                            table2.append(row);
                        });

                    } else {
                        // Aucune garantie, afficher garantie_null et cacher garantie_existe
                        $("#garantie_existe").hide();
                        $("#garantie_null").show();
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Erreur :", error);
                }
            });
        }

        afficherGarantiesSessionSinistre();

        // Surveiller les changements des cases à cocher
        $(document).on('change', '.sinistre_garantie_checkbox', function () {
            // Récupérer la ligne parente (tr) de la case cochée/décochée
            const parentRow = $(this).closest('tr');

            // Trouver les champs franchise et capital associés
            const SinistrefranchiseInput = parentRow.find('.sinistre_franchise_input');
            const SinistrecapitalInput = parentRow.find('.sinistre_capital_input');
            const SinistreprimenetInput = parentRow.find('.sinistre_prime_net_input');
            const SinistreprimettcInput = parentRow.find('.sinistre_prime_ttc_input');

            if ($(this).is(':checked')) {
                // Activer les champs si la case est cochée
                SinistrefranchiseInput.prop('disabled', false);
                SinistrecapitalInput.prop('disabled', false);
                SinistreprimenetInput.prop('disabled', false);
                SinistreprimettcInput.prop('disabled', false);
            } else {
                // Désactiver et vider les champs si la case est décochée
                SinistrefranchiseInput.prop('disabled', true).val('');
                SinistrecapitalInput.prop('disabled', true).val('');
                SinistreprimenetInput.prop('disabled', true).val('');
                SinistreprimettcInput.prop('disabled', true).val('');
            }
        });

        mettreAJourTableauSinistre();
        
        $("#btn_save_sinistre_garantie").on("click", function () {
            let garanties = [];
    
            $("#table_add_sinistre_garantie tbody .sinistre_garantie_checkbox:checked").each(function () {
                let row = $(this).closest("tr");
                let garantieId = $(this).val();
                let garantieNom = row.find("td:nth-child(2)").text();
                let franchise = row.find(".sinistre_franchise_input").val();
                let capital = row.find(".sinistre_capital_input").val();
                let primeNet = row.find(".sinistre_prime_net_input").val();
                let primeTTC = row.find(".sinistre_prime_ttc_input").val();
    
                garanties.push({
                    id: garantieId,
                    sinistre_id: sinistreId,
                    nom: garantieNom,
                    franchise: franchise,
                    capital: capital,
                    prime_net: primeNet,
                    prime_ttc: primeTTC,
                });
            });
    
            enregistrerGarantiesSinistre(garanties);
        });

        function mettreAJourTableauSinistre() {
            $.ajax({
                url: "/production/recuperer_garanties_circonstance_sinistre/",
                type: "GET",
                data: {sinistre_id: sinistreId},
                cache: false, // Désactiver le cache
                success: function (response) {
                    let table2 = $("#table_garantie_sinistre tbody");
                    table2.empty();
    
                    if (response.garanties && response.garanties.length > 0) {
                        // Garanties présentes, cacher garantie_null
                        $("#garantie_null").hide();
    
                        $.ajax({
                            url: "/production/afficher_provision_circonstance_sinistre/",
                            type: "GET",
                            data: {sinistre_id: sinistreId},
                            success: function (response) {
                                console.log(response);
                                $("#garantie_existe").show();
                                $("#garantie_existe").html(response);
                                $("#table_provision_sinistre_container").html(response);
                            },
                            error: function (xhr, status, error) {
                                console.error("Erreur lors du chargement du tableau des provisions :", error);
                            }
                        });
    
                        response.garanties.forEach(function (garantie) {
                            let row = `
                                <tr data-id="${garantie.id}">
                                    <td><span class="btn btn-danger btn-sm btn-delete-garantie" data-id="${garantie.id}"><i class="fa fa-trash-o"></i></span></td>
                                    <td>${garantie.nom}</td>
                                    <td class="text-center">${garantie.mouvement}</td>
                                    <td class="text-center">${garantie.date}</td>
                                </tr>
                            `;
                            table2.append(row);
                        });
                    } else {
                        // Aucune garantie, afficher garantie_null et cacher garantie_existe
                        $("#garantie_existe").hide();
                        $("#garantie_null").show();
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Erreur :", error);
                }
            });
        }

        $(document).off('click', '.btn-delete-garantie').on('click', '.btn-delete-garantie', function () {
            const GarantieId = $(this).data('id');
            console.log("ID de la garantie à supprimer:", GarantieId);
            let n = noty({
                text: 'Voulez-vous supprimer cette garantie ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary',
                        text: 'Confirmer',
                        onClick: function ($noty) {
                            $.ajax({
                                url: '/production/delete_garantie_session/',
                                type: 'POST',
                                contentType: 'application/json',
                                data: JSON.stringify({ garantie_id: GarantieId}),
                                success: function (response) {
                                    if (response.success) {
                                        mettreAJourTableauSinistre();
                                    } else {
                                        console.error(response.message);
                                    }
                                },
                                error: function (xhr) {
                                    console.error("Une erreur est survenue lors de la suppression de la garantie.");
                                }
                            });
                            $noty.close();
                        }
                    },
                    {
                        addClass: 'btn btn-danger',
                        text: 'Annuler',
                        onClick: function ($noty) {
                            $noty.close();
                        }
                    }
                ]
            });
        });
          
        function enregistrerGarantiesSinistre(garanties) {
            $.ajax({
                url: "/production/enregistrer_garanties_circonstance_sinistre/",
                type: "POST",
                data: {sinistre_id: sinistreId},
                headers: { "X-CSRFToken": getCSRFToken() },
                contentType: "application/json",
                data: JSON.stringify({ garanties: garanties }),
                success: function (response) {
                    if (response.success) {
                        mettreAJourTableauSinistre();
                        resetTableFormSinistre();
                    } else {
                        alert("Erreur lors de l'enregistrement.");
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Erreur :", error);
                }
            });
        }

        function resetTableFormSinistre() {
            $("#table_add_sinistre_garantie tbody tr").each(function () {
                $(this).find(".sinistre_garantie_checkbox").prop("checked", false);
                $(this).find("input[type=text]").val("").prop("disabled", true);
            });
        }

        $(document).on("keyup change", "#table_provision_sinistre .calculs_montant_garantie_sinistre", function (event) {
        if (event.which == 13) {
            event.preventDefault();
        }
        calculer_montant_garantie_sinistre();
        enregistrer_montant_garantie_sinistre($(this));
    });

        function calculer_montant_garantie_sinistre() {
            let totaux = {};  // Stocker les totaux par garantie

            $("#table_provision_sinistre tbody tr").each(function () {
                let postedommageId = $(this).find("td:first").text().trim().toLowerCase(); // Nom du poste dommage
                let isFranchise = postedommageId.includes("franchise");

                $(this).find("input").each(function () {
                    let input = $(this);
                    let idParts = input.attr("id").split("_");
                    let garantieId = idParts[idParts.length - 1];
                    let type = input.data("type");
                    let valeur = parseInt(input.val().replaceAll(' ', '')) || 0;

                    if (isFranchise) {
                        valeur *= -1;
                    }

                    // Initialiser l'objet de stockage des totaux
                    if (!totaux[garantieId]) {
                        totaux[garantieId] = { estimation: 0, deja_regle: 0, provision: 0 };
                    }
                    totaux[garantieId][type] += valeur;
                });
            });

            // Mise à jour des champs de total
            for (const [garantieId, total] of Object.entries(totaux)) {
                $(`#total_estimation_${garantieId}`).val(total.estimation.toLocaleString());
                $(`#total_deja_regle_${garantieId}`).val(total.deja_regle.toLocaleString());
                $(`#total_provision_${garantieId}`).val(total.provision.toLocaleString());
            }
        }

        function enregistrer_montant_garantie_sinistre(input) {
            let idParts = input.attr("id").split("_");
            let postedommageId = idParts[1];
            let garantieId = idParts[2];
            let type = input.data("type");
            let valeur = parseInt(input.val().replaceAll(' ', '')) || 0;

            // Vérifier si c'est "Franchise" pour inverser la valeur
            let postedommageNom = $(`#table_provision_sinistre tbody tr td:first:contains('${postedommageId}')`).text().trim().toLowerCase();
            if (postedommageNom.includes("franchise")) {
                valeur *= -1;
            }

            console.log('Poste dommage ID:', postedommageId);
            console.log('Garantie ID:', garantieId);
            console.log('Valeur envoyée:', valeur);

            $.ajax({
                url: "/production/enregistrer_montant_garantie_sinistre/",
                type: "POST",
                headers: { "X-CSRFToken": getCSRFToken() },
                contentType: "application/json",
                data: JSON.stringify({
                    postedommageId: postedommageId,
                    garantieId: garantieId,
                    type: type,
                    valeur: valeur,
                }),
                success: function (response) {
                    if (response.success) {
                        let totaux = response.totaux;

                        for (const [garantieId, total] of Object.entries(totaux)) {
                        }
                    } else {
                        console.error("Erreur lors de l'enregistrement en session.");
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Erreur de communication avec le serveur.");
                }
            });
        }

        /**** Bloc du traitement des garanties et des provisions Fin ****/

        /**** Bloc du traitement des intervenants Début ****/

        const intervenantSinistreTableBody = $('#table_intervenant_sinistre tbody');

        function chargerIntervenantsSinistre() {
            $.ajax({
                url: '/production/get_intervenants_session_sinistre/',
                type: 'GET',
                data: { sinistre_id: sinistreId },
                success: function (response) {
                    let table2 = $("#table_intervenant_sinistre tbody");
                    table2.empty();

                    if (response.intervenants && response.intervenants.length > 0) {
                        console.log('Les intervenants seront visible ici');
                        response.intervenants.forEach(function (intervenant) {
                            let row = `
                                <tr data-id="${intervenant.id}">
                                    <td><span class="btn btn-danger btn-sm btn-delete-intervenant" data-id="${intervenant.id}"><i class="fa fa-trash-o"></i></span></td>
                                    <td>${intervenant.nom || ''}</td>
                                    <td>${intervenant.prenoms || ''}</td>
                                    <td>${intervenant.typeintervenant || ''}</td>
                                    <td>${intervenant.portable || ''}</td>
                                    <td>${intervenant.email || ''}</td>
                                    <td>${intervenant.code_postal || ''}</td>
                                    <td>${intervenant.ville || ''}</td>
                                </tr>
                            `;
                            table2.append(row);
                        });
                    } else {
                        // Rien à signaler
                    }
                },
                error: function (xhr) {
                    console.error("Une erreur est survenue lors de la récupération des intervenants.");
                }
            });
        }

        chargerIntervenantsSinistre();

        $(document).off('click', '.btn-delete-intervenant').on('click', '.btn-delete-intervenant', function () {
            const intervenantId = $(this).data('id');

            let n = noty({
                text: 'Voulez-vous supprimer cet intervenant ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary',
                        text: 'Confirmer',
                        onClick: function ($noty) {
                            $.ajax({
                                url: '/production/delete_intervenant_session_sinistre/',
                                type: 'POST',
                                contentType: 'application/json',
                                data: JSON.stringify({ intervenant_id: intervenantId, sinistre_id: sinistreId }),
                                success: function (response) {
                                    if (response.success) {
                                        chargerIntervenantsSinistre();
                                        // Affiche un message de succès à l'utilisateur
                                        $('#intervenant-modal-success').text("Intervenant supprimé avec succès !").show().delay(3000).fadeOut();
                                    } else {
                                        console.error(response.message);
                                        // Affiche un message d'erreur à l'utilisateur
                                        $('#intervenant-modal-error').text("Erreur lors de la suppression de l'intervenant : " + response.message).show().delay(5000).fadeOut();
                                    }
                                },
                                error: function (xhr) {
                                    console.error("Une erreur est survenue lors de la suppression de l'intervenant.");
                                    // Affiche un message d'erreur à l'utilisateur
                                    $('#intervenant-modal-error').text("Une erreur est survenue lors de la suppression de l'intervenant.").show().delay(5000).fadeOut();
                                }
                            });
                            $noty.close();
                        }
                    },
                    {
                        addClass: 'btn btn-danger',
                        text: 'Annuler',
                        onClick: function ($noty) {
                            $noty.close();
                        }
                    }
                ]
            });
        });

        $('#btn_save_sinistre_intervenant').off('click').on('click', function () {
            $('.intervenant_champ_obligatoire').removeClass('is-invalid is-valid');
            $('#intervenant-modal-error, #intervenant-modal-warning, #intervenant-modal-success').text('').hide();

            let valide = true;
            $('.intervenant_champ_obligatoire').each(function () {
                let value = $(this).val().trim();
                if (!value) {
                    $(this).addClass('is-invalid');
                    valide = false;
                } else {
                    $(this).removeClass('is-invalid').addClass('is-valid');
                }
            });

            if (!valide) {
                $('#intervenant-modal-error').text('Veuillez remplir tous les champs obligatoires.').show();
                return;
            }

            const formData = new FormData($('#form_add_sinistre_intervenant')[0]);
            formData.append('sinistre_id', sinistreId);

            $.ajax({
                url: '/production/add_intervenant_session_sinistre/',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    if (response.success) {
                        $("#intervenant-modal-success").text(response.message).show();
                        chargerIntervenantsSinistre();
                        setTimeout(() => {
                            $("#form_add_sinistre_intervenant").trigger("reset");
                            $('.intervenant_champ_obligatoire').removeClass('is-valid is-invalid');
                            $("#intervenant-modal-success").fadeOut();
                        }, 3000);
                    } else {
                        $("#intervenant-modal-warning").text(response.message).show().delay(5000).fadeOut();
                    }
                },
                error: function (xhr) {
                    const response = xhr.responseJSON;
                    $("#intervenant-modal-error").text(response?.message || "Une erreur est survenue.").show().delay(5000).fadeOut();
                },
            });
        });

        /**** Bloc du traitement des intervenants Fin ****/

    });
});
$(document).ready(function () {

    function alert_pop() {
        alert("open modal benef");
    }
    //dérouler le menu prise en charge
    //
    if (typeof $.fn.select2 === 'function') {

        $('.tags-multiple').select2();
        $('.select2-container').css({
            'width': '100%'
        });
        $('.select2-container--default').css({
            'color': 'black'
        });
        $('.select2-container--multiple').css({
            'color': 'black'
        });
        $('.select2-container__choice').css({
            'color': 'black'
        });
    }

    //init datatables
    $('.dataTable:not(.customDataTable)').DataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"
        },
        order: [[0, 'desc']],
        lengthMenu: [
            [10, 25, 50, -1],
            [10, 25, 50, 'Tout'],
        ]
    });

    $('#table_apporteurs_details_police').DataTable({
        order: [[0, 'desc']],
        sDom: "<'row'<'col-sm-6'>>t<'row'<'col-sm-6'><'col-sm-6'>>",
        paging: true,
        searching: true,
        lengthChange: true,
    });

    $('#table_garantie_details_police').DataTable({
        order: [[0, 'desc']],
        sDom: "<'row'<'col-sm-6'>>t<'row'<'col-sm-6'><'col-sm-6'>>",
        paging: true,
        searching: true,
        lengthChange: true,
    });

    $('#table_bordereau_paiement').DataTable({
        order: [[0, 'desc']],
        sDom: "<'row'<'col-sm-6'>>t<'row'<'col-sm-6'><'col-sm-6'>>",
        paging: true,
        searching: true,
        lengthChange: true,
    });


    if ($('#accordionClient').length) {
        showCurentTab();
    } else {
        localStorage.removeItem('active_button');
        localStorage.removeItem('active_collapse');
    }

    // using jQuery
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

    $.ajaxSetup({ headers: { "X-CSRFToken": csrftoken } });


    $(document).on('click', "#accordionClient .info-box", function () {

        //sauvegarder pour afficher le meme onglet si on recharge/actualise la page
        localStorage.setItem("active_button", $(this).attr('id'));
        localStorage.setItem("active_collapse", $(this).attr('href'));

        //Afficher l'onglet sélectionné
        showCurentTab();


    });


    function ucfirst(string) {
        return string[0].toUpperCase() + string.slice(1);
    }

    //Afficher le contenu de l'onglet actif
    function showCurentTab() {

        let active_button = localStorage.getItem("active_button");
        let active_collapse = localStorage.getItem("active_collapse");

        if (active_button != null && active_collapse != null) {

            //les libellés
            $("#accordionClient .info-box").removeClass('active');

            $('#' + active_button).addClass('active');


            //les contenus
            $("#accordionClient .collapse").hide();

            $(active_collapse).show();

        }

    }


    //****************** INTERFACE CLIENT ******************//

    //----------- AJOUT, MODIFICATION DU CLIENT ------------//

    //ajout d'un client
    //gestion selection type personne (morale, physique)
    function manage_type_personne_change() {

        let type_personne_id = parseInt($('#modal-client #type_personne_id').val());

        $('.champ_variable_client').hide();
        $('.champ_variable_client input').removeAttr('required')
        $('.champ_variable_client select').removeAttr('required')

        switch (type_personne_id) {
            default:
            case 1://personne physique
                $('.if_personne_physique').show();
                $('.if_personne_physique input').attr('required', 'required');
                $('.if_personne_physique select').attr('required', 'required');
                $('#commercial_id').closest('.form-group').hide();
                $('#groupe_id').closest('.form-group').hide();
                $('#date_naissance').closest('.form-group').show();
                $('#date_creation').closest('.form-group').hide();
                break;
            case 2://personne morale
                $('.if_personne_morale').show();
                $('.if_personne_morale input').attr('required', 'required');
                $('.if_personne_morale select').attr('required', 'required');
                $('#commercial_id').closest('.form-group').show();
                $('#groupe_id').closest('.form-group').show();
                $('#date_naissance').closest('.form-group').hide();
                $('#date_creation').closest('.form-group').show();
                break;
        }
    }

    manage_type_personne_change();
    $(document).on('change', "#modal-client #type_personne_id", function () {
        manage_type_personne_change();
    });

    //modification
    function manage_type_personne_change_modification() {

        let type_personne_id = parseInt($('#modal-modification_client #type_personne_id').val());

        $('.champ_variable_client').hide();
        $('.champ_variable_client input').removeAttr('required')
        $('.champ_variable_client select').removeAttr('required')

        switch (type_personne_id) {
            default:
            case 1://personne physique
                $('.if_personne_physique').show();
                $('.if_personne_physique input').attr('required', 'required');
                $('.if_personne_physique select').attr('required', 'required');
                $('#commercial_id').closest('.form-group').hide();
                $('#groupe_id').closest('.form-group').hide();
                $('#date_naissance').closest('.form-group').show();
                $('#date_creation').closest('.form-group').hide();
                break;
            case 2://personne morale
                $('.if_personne_morale').show();
                $('.if_personne_morale input').attr('required', 'required');
                $('.if_personne_morale select').attr('required', 'required');
                $('#commercial_id').closest('.form-group').show();
                $('#groupe_id').closest('.form-group').show();
                $('#date_naissance').closest('.form-group').hide();
                $('#date_creation').closest('.form-group').show();
                break;
        }
    }

    manage_type_personne_change_modification();
    $(document).on('change', "#modal-modification_client #type_personne_id", function () {
        manage_type_personne_change_modification();
    });

    $(document).on('click', "#btn_save_client", function () {

        let formulaire = $('#form_add_client');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();
        let files = $('#form_add_client #logo_client')[0].files;

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer ce client ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu
                            if (files.length > 0) {
                                formData.append('logo_client', files[0]);
                            }

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {
                                        //Vider le formulaire
                                        resetFields('#' + formulaire.attr('id'));

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-client .alert .message').html(errors_list_to_display);

                                        $('#modal-client .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });
                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //modification d'un client
    $(document).on('click', '.btn_modifier_client', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            manage_type_personne_change_modification();

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_client').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_client').find('.modal-title').text(modal_title);
            $('#modal-modification_client').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_client').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-modification_client').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_client").on('click', function () {

                let formulaire = $('#form_update_client');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();
                let files = $('#form_update_client #logo_client')[0].files;

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier ce client ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    if (files.length > 0) {
                                        formData.append('logo', files[0]);
                                    }

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_client .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_client .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });
                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //fin modification d'un client

    //suppression un client
    $(document).on('click', '.btn_supprimer_client', function () {
        let client_id = $(this).data('client_id');

        let n = noty({
            text: 'Voulez-vous vraiment supprimer ce client ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: '/production/client/delete',
                            type: 'post',
                            data: { client_id: client_id },
                            success: function (e) {

                                location.reload();

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });
    //fin suppression d'un client


    //----------- FIN AJOUT, MODIFICATION DU CLIENT ------------//


    //----------------- AJOUT DE CONTACT ------------------//
    // TODO AJOUT DE CONTACT DU CLIENT
    //Création d'une contact
    $(document).on('click', "#btn_contact_client", function () {

        let formulaire = $('#form_contact_client');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer cette contact ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            formulaire[0].reset(); // Réinitialise tous les champs du formulaire
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-client .alert .message').html(errors_list_to_display);

                                        $('#modal-client .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });
                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un contact
    $(document).on('click', '.btn_modifier_contact', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_contact').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_contact').find('.modal-title').text(modal_title);
            $('#modal-modification_contact').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_contact').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_contact').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_contact").on('click', function () {

                let formulaire = $('#form_update_contact');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cet contact ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_contact .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_contact .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });
                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un contact
    $(document).on('click', '.btn_supprimer_contact', function () {
        let contact_id = $(this).data('contact_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette contact ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { contact_id: contact_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });


    //----------------- FIN AJOUT DE CONTACT ------------------//


    //----------------- AJOUT DE FILIALE ------------------//

    // TODO AJOUT DE FILIALE DU CLIENT
    //Création d'une filiale
    $(document).on('click', "#btn_filiale_client", function () {

        let formulaire = $('#form_filiale_client');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer cette contact ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            formulaire[0].reset(); // Réinitialise tous les champs du formulaire
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-client .alert .message').html(errors_list_to_display);

                                        $('#modal-client .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });
                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une filiale
    $(document).on('click', '.btn_modifier_filiale', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_filiale').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_filiale').find('.modal-title').text(modal_title);
            $('#modal-modification_filiale').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_filiale').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_filiale').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_filiale").on('click', function () {

                let formulaire = $('#form_update_filiale');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cette filiale ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_filiale .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_filiale .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une filiale
    $(document).on('click', '.btn_supprimer_filiale', function () {
        let filiale_id = $(this).data('filiale_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette filiale ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { filiale_id: filiale_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //----------------- FIN AJOUT DE FILIALE ------------------//


    //----------------- AJOUT DE DOCUMENT ------------------//
    //Création d'un document
    $(document).on('click', "#btn_save_document_client", function () {

        let formulaire = $('#form_document_client');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();
        let files = $('#form_document_client #fichier')[0].files;

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer cette contact ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu
                            if (files.length > 0) {
                                formData.append('fichier', files[0]);
                            }

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            formulaire[0].reset(); // Réinitialise tous les champs du formulaire
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-client .alert .message').html(errors_list_to_display);

                                        $('#modal-client .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });
                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
        }

        else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un document
    $(document).on('click', '.btn_modifier_document', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_document').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_document').find('.modal-title').text(modal_title);
            $('#modal-modification_document').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_document').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_document').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_document_client").on('click', function () {

                let formulaire = $('#form_modification_document_client');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();
                let files = $('#form_modification_document_client #fichier')[0].files;

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cette document ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu
                                    if (files.length > 0) {
                                        formData.append('fichier', files[0]);
                                    }

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_document .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_document .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un document
    $(document).on('click', '.btn_supprimer_document', function () {
        let document_id = $(this).data('document_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette document ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { document_id: document_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    $(document).on("click", "#btn_save_document_dossier_sinistre", function () {

        const button = $(this); // Sauvegarder le bouton cliquÃ©
        button.prop('disabled', true).text(gettext('Chargement')); // DÃ©sactive le bouton et change le texte

        let modal_id = $(this).closest('.modal').attr('id');

        let formulaire = $(this).closest('form');
        $.validator.setDefaults({ ignore: [] });

        let action_url = $(this).closest('form').attr('action');

        let dossier_sinistre_id = $('#' + modal_id + ' #dossier_sinistre_id').val();

        let formData = new FormData();

        let form_validity = false

        for (let i = 0; i < 6; i++) {
            file = $('#' + modal_id + ' #fichier_' + i)[0].files[0];
            type_document = $('#' + modal_id + ' #type_document_' + i).val();
            console.log(file);
            console.log(type_document);
            if (file) {
                form_validity = true;
                formData.append('fichier_' + i, file);
                formData.append('type_document_' + i, type_document);
            }
        }

        if (form_validity == true) {

            formData.append('dossier_sinistre_id', dossier_sinistre_id);

            $.ajax({
                type: 'post',
                url: action_url,
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    //console.log(response);
                    //return false;
                    if (response.statut == 1) {
                        for (var d = 0; d < response.documents.length; d++) {
                            //mettre Ã  jour le tableau
                            let document = response.documents[d];
                            let t = $('#table_documents').DataTable();
                            t.row.add([document.type_document, document.fichier, '<td class=""><span class="btn_delete_document_dossier_sinistre" id="btn_delete_document_dossier_sinistre" data-document_id="' + document.id + '" onClick="dossier_sinistre_supprimer_document(' + document.id + ')" style="cursor:pointer;"><i class="fa fa-times text-danger"></i></span></td>']).draw(false);

                            //Afficher le message de succÃ¨s et fermer la fenÃªtre
                            $('#' + modal_id + ' input[type=file]').val("");
                            $('#' + modal_id + ' input[type=text]').val("");
                            $('#' + modal_id + ' textarea').val("");
                            $('#' + modal_id + ' select').prop('selectedIndex', 0);
                        }
                        $('#' + modal_id).modal('hide');
                        notifySuccess(response.message, function () {
                            location.reload();
                        });
                    } else {

                        $('#' + modal_id + ' .alert .message').text(response.message);

                        $('#' + modal_id + ' .alert ').fadeTo(2000, 500).slideUp(500, function () {
                            $(this).slideUp(500);
                        }).removeClass('alert-success').addClass('alert-warning');

                    }


                },
                error: function () {

                    button.prop('disabled', false).text('Valider');

                    $('#' + modal_id + ' .alert .message').text(gettext("Erreur lors de l'enregistrement !"));

                    $('#' + modal_id + ' .alert ').fadeTo(2000, 500).slideUp(500, function () {
                        $(this).slideUp(500);
                    }).removeClass('alert-success').addClass('alert-warning');

                }
            });

        } else {
            notifyWarning(gettext("Veuillez charger au moins un fichier"));
            button.prop('disabled', false).text('Valider');
        }

    });

    $(document).on("click", ".btn_delete_document_dossier_sinistre", function (e) {
        let document_id = $(this).data('document_id');
        let href = '/sinistre/dossier_sinistre_document/delete';

        //demander confirmation
        let n = noty({
            text: gettext('Voulez-vous vraiment supprimer ce document ?'),
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: gettext('OUI'), onClick: function ($noty) {
                        $noty.close();

                        //confirmation obtenu
                        $.ajax({
                            type: 'post',
                            url: href,
                            data: { document_id: document_id },
                            success: function (response) {

                                if (response.statut == 1) {

                                    notifySuccess(response.message, function () {
                                        location.reload();
                                    });

                                } else {
                                    notifyWarning(gettext("Erreur lors de la suppression du tarif"));
                                }

                            },
                            error: function (request, status, error) {

                                notifyWarning(gettext("Erreur lors du traitement"));
                            }

                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: gettext('Annuler'), onClick: function ($noty) {
                        //confirmation refusÃ©e
                        $noty.close();

                    }
                }
            ]
        });
        //fin demande confirmation

    });


    //----------------- FIN AJOUT DE DOCUMENT ------------------//

    //----------------- DEBUT AJOUT INTERVENANT SINISTRE ------------------//

    //Détails d'un intervenant
    $(document).on('click', '.btn_details_intervenant', function () {
        let model_name = $(this).attr('data-model_name');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            $('#modal-details_intervenant').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-details_intervenant').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-details_intervenant').find('.modal-dialog').addClass('modal-lg').removeClass('modal-lg');

            //
            $('#modal-details_intervenant').modal();

        });
    });
    //----------------- FIN AJOUT INTERVENANT SINISTRE ------------------//


    // TODO ACOMPTE DU CLIENT
    //Ajout acompte
    $("#btn_client_acompte").on('click', function () {

        let btn_client_acompte = $(this);

        let formulaire = $('#form_acompte_client');

        let montant = parseFloat($('#montant').val());
        let periode_debut = $('#periode_debut').val();
        let periode_fin = $('#periode_fin').val();

        $.validator.setDefaults({ ignore: [] });

        if (formulaire.valid()) {
            // Vérifie si le montant est valide
            if (isNaN(montant) || montant <= 0) {
                notifyWarning('Le montant doit être un nombre supérieur à 0.');
                return;
            }

            if (periode_debut && !periode_fin) {
                notifyWarning('La période fin est obligatoire lorsque la période début est renseignée.');
                return;
            }

            if (new Date(periode_debut) > new Date(periode_fin)) {
                notifyWarning('La période début doit être antérieure ou égale à la période fin.');
                return;
            }

            $.ajax({
                type: 'post',
                url: formulaire.attr('action'),
                data: $('#form_acompte_client').serialize(),
                success: function (response) {

                    if (response.statut == 1) {

                        notifySuccess(response.message, function () {
                            formulaire[0].reset(); // Réinitialise tous les champs du formulaire
                            location.reload();
                        });

                    } else {
                        notifyWarning(response.message);
                    }

                },
                error: function (response) {
                    console.log(response);
                    btn_client_acompte.show();
                }
            });

        } else {
            let validator = formulaire.validate();
            notifyWarning("Veuillez renseigner tout les champs obligatoire");
        }

    });

    //Modification d'un acompte
    $(document).on('click', '.btn_modifier_acompte', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_acompte').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_acompte').find('.modal-title').text(modal_title);
            $('#modal-modification_acompte').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_acompte').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_acompte').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_acompte").on('click', function () {

                let formulaire = $('#form_update_acompte');
                let href = formulaire.attr('action');

                let montant = parseFloat($('#montant_modification').val().replace(' ', ''));
                let periode_debut = $('#periode_debut_modification').val().trim();
                let periode_fin = $('#periode_fin_modification').val().trim();

                // Vérifie si le montant est valide
                if (isNaN(montant) || montant <= 0) {
                    notifyWarning('Le montant doit être un nombre supérieur à 0.');
                    return;
                }

                if (periode_debut && !periode_fin) {
                    notifyWarning('La période fin est obligatoire lorsque la période début est renseignée.');
                    return;
                }

                if (new Date(periode_debut) > new Date(periode_fin)) {
                    notifyWarning('La période début doit être antérieure ou égale à la période fin.');
                    return;
                }

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {
                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cet acompte ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            }
                                            if(response.statut == 0){

                                                notifyWarning(response.message);

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Supprimer acompte
    $(document).on('click', '.btn_supprimer_acompte', function () {
        let acompte_id = $(this).data('acompte_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette acompte ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { acompte_id: acompte_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //TRAITEMENT PAGE POLICE

    // Ajoutez un gestionnaire d'événements au changement de la police
    $('#police_sortante_id').change(function () {
        // Récupérez la valeur sélectionnée
        var policeId = $(this).val();


        var href = $(this).data('href').replace('0', policeId);

        // Effectuez une requête AJAX pour récupérer les formules associées
        $.ajax({
            url: href,
            type: 'GET',
            dataType: 'json', // Assurez-vous que votre vue renvoie du JSON
            success: function (data) {
                // Mettre à jour le contenu du menu déroulant formules de la police choisi
                var formuleDropdown = $('#formule_sortante_code');
                formuleDropdown.empty();
                $.each(data.formules, function (key, formule) {
                    formuleDropdown.append('<option value="' + formule.code + '">' + formule.libelle + '</option>');
                });
            },
            error: function () {
                console.error('Erreur lors de la récupération des formules.');
            }
        });
    });

    // TODO CHANGEMENT DE COMPAGNIE
    $("#btn_valider_changement_compagnie").on('click', function () {

        let btn_valider_changement_compagnie = $(this);

        let formulaire = $('#form_changement_compagnie');

        $.validator.setDefaults({ ignore: [] });

        if (formulaire.valid()) {

            $.ajax({
                type: 'post',
                url: formulaire.attr('action'),
                data: $('#form_changement_compagnie').serialize(),
                beforeSend: function () {
                    $('#loading_gif').show();
                    btn_valider_changement_compagnie.hide();
                },
                success: function (response) {

                    $('#loading_gif').hide();
                    //btn_valider_changement_compagnie.hide();

                    if (response.statut == 1) {

                        notifySuccess(response.message, function () {
                            location.reload();
                        });

                    } else {
                        notifyWarning(response.message);
                    }

                },
                error: function (response) {
                    console.log(response);
                    btn_valider_changement_compagnie.show();
                }
            });

        } else {
            let validator = formulaire.validate();
            notifyWarning("Veuillez sélectionner les polices");
        }

    });


    //gestion changement de genre/sexe
    $(document).on('click', '#genre', function () {

        let genre = $(this).val();

        if (genre == 'F') {
            $('#box_nom_jeune_fille').show();
        } else {
            $('#box_nom_jeune_fille').hide();
        }

    });
    //fin gestion changement de genre/sexe

    //Ajout de véhicule
    $(document).on('click', "#btn_save_vehicule", function () {

        let formulaire = $('#form_add_vehicule');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            let data_serialized = formulaire.serialize();
            $.each(data_serialized.split('&'), function (index, elem) {
                let vals = elem.split('=');

                let key = vals[0];
                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                formData.append(key, valeur);

            });

            $.ajax({
                type: 'post',
                url: href,
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {

                    if (response.statut == 1) {

                        notifySuccess(response.message);
                        location.reload();

                    } else {

                        let errors = JSON.parse(JSON.stringify(response.errors));
                        let errors_list_to_display = '';
                        for (field in errors) {
                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                        }

                        $('#modal-vehicule .alert .message').html(errors_list_to_display);

                        $('#modal-vehicule .alert ').fadeTo(2000, 500).slideUp(500, function () {
                            $(this).slideUp(500);
                        }).removeClass('alert-success').addClass('alert-warning');

                    }

                },
                error: function (request, status, error) {

                    notifyWarning("Erreur lors de l'enregistrement");
                }

            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner tous les champs obligatoires');
        }


    });


    $(document).on('click', '.btn_modifier_vehicule', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_vehicule').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_vehicule').find('.modal-title').text(modal_title);
            $('#modal-modification_vehicule').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_vehicule').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-modification_vehicule').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_vehicule").on('click', function () {

                let formulaire = $('#form_update_vehicule');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    let data_serialized = formulaire.serialize();
                    $.each(data_serialized.split('&'), function (index, elem) {
                        let vals = elem.split('=');

                        let key = vals[0];
                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                        formData.append(key, valeur);

                    });

                    $.ajax({
                        type: 'post',
                        url: href,
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function (response) {

                            if (response.statut == 1) {

                                notifySuccess(response.message);
                                location.reload();

                            } else {

                                let errors = JSON.parse(JSON.stringify(response.errors));
                                let errors_list_to_display = '';
                                for (field in errors) {
                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                }

                                $('#modal-vehicule .alert .message').html(errors_list_to_display);

                                $('#modal-vehicule .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                    $(this).slideUp(500);
                                }).removeClass('alert-success').addClass('alert-warning');

                            }

                        },
                        error: function (request, status, error) {

                            notifyWarning("Erreur lors de l'enregistrement");
                        }

                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });


        });

    });


    $(document).on('click', ".btn_supprimer_vehicule", function () {

        let vehicule_id = $(this).data('vehicule_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer ce vehicule ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { vehicule_id: vehicule_id },
                            success: function (e) {

                                location.reload();

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression du vehicule');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });

    });

    //changement de formule
    $(document).on("click", "#btn_save_changement_formule", function (e) {
        e.stopPropagation();

        let btn_valider = $(this);

        let formulaire = $('#form_changement_formule');
        let href = formulaire.attr('action');

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment changer de formule ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            btn_valider.prop('disabled', true).attr('disabled', true);

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formulaire.serialize(),
                                success: function (response) {

                                    btn_valider.removeAttr('disabled');

                                    if (response.statut == 1) {

                                        //Fermer le modal
                                        $('#modal-changement_formule').modal('hide');

                                        avenant = response.data;
                                        let t = $('#table_avenants_beneficiaire').DataTable();

                                        t.row.add([
                                            avenant.libelle,
                                            avenant.date_effet,
                                            avenant.motif,
                                            avenant.created_by
                                        ])
                                            .draw(false);

                                        $("#date_fin_aliment_formule_" + avenant.old_id).html(avenant.old_date_fin);

                                        //ligne de formules
                                        aliment_police = response.data;

                                        let tcf = $('#table_forumules').DataTable();

                                        tcf.row.add([
                                            aliment_police.formule_libelle_formule,
                                            aliment_police.formule_code_formule,
                                            aliment_police.date_effet,
                                            '',
                                            ''
                                        ])
                                            .draw(false);

                                        tcf.order([0, 'desc']).draw();

                                        //Vider le formulaire
                                        resetFields('#' + formulaire.attr('id'));

                                        notifySuccess(response.message);
                                        //location.reload();

                                    } else {
                                        notifyWarning(response.message);

                                    }

                                },
                                error: function (request, status, error) {
                                    btn_valider.removeAttr('disabled');
                                    notifyWarning("Erreur lors de l'enregistrement" + request.responseText);
                                }

                            });



                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            btn_valider.removeAttr('disabled');

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner tous les champs obligatoires');
        }

    });

    $(document).on("click", "#btn_save_remise_en_vigueur", function (e) {

        e.stopPropagation();

        let btn_valider = $(this);
        let ligne_tr = $(this).closest('tr');

        let formulaire = $('#form_remise_en_vigueur');
        let href = formulaire.attr('action');

        if (formulaire.valid()) {

            btn_valider.prop('disabled', true).attr('disabled', true);

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment le remettre en vigueur le bénéficiaire ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formulaire.serialize(),
                                success: function (response) {

                                    btn_valider.removeAttr('disabled');

                                    if (response.statut == 1) {

                                        //Fermer le modal
                                        $('#modal-remise_en_vigueur').modal('hide');

                                        avenant = response.data;
                                        let t = $('#table_avenants_beneficiaire').DataTable();

                                        t.row.add([
                                            avenant.libelle,
                                            avenant.date_effet,
                                            avenant.motif,
                                            avenant.created_by
                                        ])
                                            .draw(false);


                                        //Vider le formulaire
                                        resetFields('#' + formulaire.attr('id'));

                                        notifySuccess(response.message);

                                    } else {

                                    }

                                },
                                error: function (request, status, error) {
                                    btn_valider.removeAttr('disabled');
                                    notifyWarning("Erreur lors de l'enregistrement" + request.responseText);
                                }

                            });

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation
            btn_valider.prop('disabled', false).attr('disabled', false);
            btn_valider.removeAttr('disabled');

        } else {

            btn_valider.removeAttr('disabled');

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner tous les champs obligatoires');
        }

    });


    $(document).on("click", "#btn_save_sortie_police", function (e) {

        e.stopPropagation();

        let btn_valider = $(this);

        let ligne_tr = $(this).closest('tr');

        let formulaire = $('#form_sortie_police');
        let href = formulaire.attr('action');

        if (formulaire.valid()) {

            btn_valider.prop('disabled', true).attr('disabled', true);

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment le sortir de la police ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formulaire.serialize(),
                                success: function (response) {

                                    btn_valider.removeAttr('disabled');

                                    if (response.statut == 1) {

                                        //Fermer le modal
                                        $('#modal-sortie_police').modal('hide');

                                        avenant = response.data;
                                        let t = $('#table_avenants_beneficiaire').DataTable();

                                        t.row.add([
                                            avenant.libelle,
                                            avenant.date_effet,
                                            avenant.motif,
                                            avenant.created_by
                                        ])
                                            .draw(false);


                                        //Vider le formulaire
                                        resetFields('#' + formulaire.attr('id'));

                                        notifySuccess(response.message, function () {
                                            location.href = '';
                                        });

                                    } else {

                                        notifyWarning(response.message);

                                    }

                                },
                                error: function (request, status, error) {
                                    btn_valider.removeAttr('disabled');
                                    notifyWarning("Erreur lors de l'enregistrement" + request.responseText);
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation
            btn_valider.prop('disabled', false).attr('disabled', false);
            btn_valider.removeAttr('disabled');

        }

    });


    //DETAILS de vehicule
    $(document).on("click", ".btn_details_vehicule", function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        //let dialog_box = $("<div>").addClass('olea_std_dialog_box').appendTo('body');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-details_vehicule .dataTable:not(.customDataTable_)').DataTable({
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"
                },
                order: [[0, 'desc']],
                lengthMenu: [
                    [10],
                    [10],
                ],
                searching: false,
                lengthChange: false,
            });

            let i = 0;
            $('.dropzone_area').each(function (myElement) {
                let zone_id = $(this).attr('id');
                let href = $(this).attr('action');

                let dropzone = new Dropzone("#" + zone_id, { url: href, dictDefaultMessage: "" });

            });

            $('#modal-details_vehicule').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-details_vehicule').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-details_vehicule').modal();

        });

    });


    // Importation véhicules
    $("#btn_importer_vehicules").on('click', function () {

        let href = $(this).attr('data-href');
        let formulaire = $('#modal_form_import_vehicules');

        let formData = new FormData();
        let files = $('#modal_form_import_vehicules #fichier')[0].files;
        let police_id = $('#modal_form_import_vehicules #police_id').val();

        if (files.length > 0) {

            formData.append('police_id', police_id);
            formData.append('fichier', files[0]);

            $.ajax({
                type: 'post',
                url: href,
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {

                    if (response.statut == 1) {

                        //Vider le formulaire
                        resetFields('#' + formulaire.attr('id'));

                        notifySuccess(response.message, function () {
                            location.reload();
                        });

                    } else {

                        let errors = JSON.parse(JSON.stringify(response.errors));
                        let errors_list_to_display = '';
                        for (field in errors) {
                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                        }

                        $('#modal-import_vehicules .alert .message').html(errors_list_to_display);

                        $('#modal-import_vehicules .alert ').fadeTo(2000, 500).slideUp(500, function () {
                            $(this).slideUp(500);
                        }).removeClass('alert-success').addClass('alert-warning');

                    }

                },
                error: function () {

                }
            });

        } else {
            notifyWarning('Veuillez chosisr un fichier');
        }


    });

    //DETAILS de marchandise
    $(document).on("click", ".btn_details_marchandise", function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        //let dialog_box = $("<div>").addClass('olea_std_dialog_box').appendTo('body');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-details_marchandise .dataTable:not(.customDataTable_)').DataTable({
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"
                },
                order: [[0, 'desc']],
                lengthMenu: [
                    [100],
                    [100],
                ],
                searching: false,
                lengthChange: false,
            });

            let i = 0;
            $('.dropzone_area').each(function (myElement) {
                let zone_id = $(this).attr('id');
                let href = $(this).attr('action');

                let dropzone = new Dropzone("#" + zone_id, { url: href, dictDefaultMessage: "" });

            });

            $('#modal-details_marchandise').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-details_marchandise').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-details_marchandise').modal();

        });
    });


    //Modification de marchandise
    $(document).on('click', '.btn_modifier_marchandise', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_marchandise').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_marchandise').find('.modal-title').text(modal_title);
            $('#modal-modification_marchandise').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_marchandise').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-modification_marchandise').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_marchandise").on('click', function () {

                let formulaire = $('#form_update_marchandise');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    let data_serialized = formulaire.serialize();
                    $.each(data_serialized.split('&'), function (index, elem) {
                        let vals = elem.split('=');

                        let key = vals[0];
                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                        formData.append(key, valeur);

                    });

                    $.ajax({
                        type: 'post',
                        url: href,
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function (response) {

                            if (response.statut == 1) {

                                notifySuccess(response.message);
                                location.reload();

                            }
                             if (response.statut == 2) {

                                notifyWarning(response.message);

                            } else {

                                let errors = JSON.parse(JSON.stringify(response.errors));
                                let errors_list_to_display = '';
                                for (field in errors) {
                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                }

                                $('#modal-vehicule .alert .message').html(errors_list_to_display);

                                $('#modal-vehicule .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                    $(this).slideUp(500);
                                }).removeClass('alert-success').addClass('alert-warning');

                            }

                        },
                        error: function (request, status, error) {

                            notifyWarning("Erreur lors de l'enregistrement");
                        }

                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }
            });
        });
    });


    //Suppression de marchandise
    $(document).on('click', ".btn_supprimer_marchandise", function () {

        let police_id = $(this).data('police_id');
        let marchandise_id = $(this).data('marchandise_id');
        let href = $(this).data('href');
        //alert(href);
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette marchandise ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { police_id: police_id, marchandise_id: marchandise_id },
                            success: function (e) {
                                notifySuccess("Marchandise non trouvée !");
                                location.reload();
                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression de la marchandise');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });



    });


    //DETAILS de l'historique de la marchandise
    $(document).on("click", ".btn_details_histo_marchandise", function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        //let dialog_box = $("<div>").addClass('olea_std_dialog_box').appendTo('body');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-details_marchandise_histo .dataTable:not(.customDataTable_)').DataTable({
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"
                },
                order: [[0, 'desc']],
                lengthMenu: [
                    [100],
                    [100],
                ],
                searching: false,
                lengthChange: false,
            });

            let i = 0;
            $('.dropzone_area').each(function (myElement) {
                let zone_id = $(this).attr('id');
                let href = $(this).attr('action');

                let dropzone = new Dropzone("#" + zone_id, { url: href, dictDefaultMessage: "" });

            });

            $('#modal-details_marchandise_histo').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-details_marchandise_histo').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-details_marchandise_histo').modal();

        });
    });

    //Ajout d'autre risque
    $(document).on('click', "#btn_save_autrerisque", function () {

        let formulaire = $('#form_add_autrerisque');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            let data_serialized = formulaire.serialize();
            $.each(data_serialized.split('&'), function (index, elem) {
                let vals = elem.split('=');

                let key = vals[0];
                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                formData.append(key, valeur);

            });

            $.ajax({
                type: 'post',
                url: href,
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {

                    if (response.statut == 1) {

                        notifySuccess(response.message);
                        location.reload();

                    } else {

                        let errors = JSON.parse(JSON.stringify(response.errors));
                        let errors_list_to_display = '';
                        for (field in errors) {
                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                        }

                        $('#modal-autrerisque_add .alert .message').html(errors_list_to_display);

                        $('#modal-autrerisque_add .alert ').fadeTo(2000, 500).slideUp(500, function () {
                            $(this).slideUp(500);
                        }).removeClass('alert-success').addClass('alert-warning');

                    }

                },
                error: function (request, status, error) {

                    notifyWarning("Erreur lors de l'enregistrement");
                }

            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner tous les champs obligatoires');
        }

    });


    //DETAILS d'autres risques
    $(document).on("click", ".btn_details_autrerisque", function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        //let dialog_box = $("<div>").addClass('olea_std_dialog_box').appendTo('body');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-details_autrerisque .dataTable:not(.customDataTable_)').DataTable({
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"
                },
                order: [[0, 'desc']],
                lengthMenu: [
                    [100],
                    [100],
                ],
                searching: false,
                lengthChange: false,
            });

            let i = 0;
            $('.dropzone_area').each(function (myElement) {
                let zone_id = $(this).attr('id');
                let href = $(this).attr('action');

                let dropzone = new Dropzone("#" + zone_id, { url: href, dictDefaultMessage: "" });

            });

            $('#modal-details_autrerisque').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-details_autrerisque').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-details_autrerisque').modal();

        });
    });


    //Modification d'autres risques
    $(document).on('click', '.btn_modifier_autrerisque', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_autrerisque').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_autrerisque').find('.modal-title').text(modal_title);
            $('#modal-modification_autrerisque').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_autrerisque').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-modification_autrerisque').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_autrerisque").on('click', function () {

                let formulaire = $('#form_update_autrerisque');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();
                let files = $('#form_update_autrerisque #fichier_contrat')[0].files;
                console.log('files : ', files);

                if (formulaire.valid()) {

                    if (files.length > 0) {
                        formData.append('fichier_contrat', files[0]);
                    }

                    let data_serialized = formulaire.serialize();
                    $.each(data_serialized.split('&'), function (index, elem) {
                        let vals = elem.split('=');

                        let key = vals[0];
                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                        formData.append(key, valeur);

                    });

                    $.ajax({
                        type: 'post',
                        url: href,
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function (response) {

                            if (response.statut == 1) {

                                notifySuccess(response.message);
                                location.reload();

                            }
                             if (response.statut == 2) {

                                notifyWarning(response.message);

                            } else {

                                let errors = JSON.parse(JSON.stringify(response.errors));
                                let errors_list_to_display = '';
                                for (field in errors) {
                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                }

                                $('#modal-vehicule .alert .message').html(errors_list_to_display);

                                $('#modal-vehicule .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                    $(this).slideUp(500);
                                }).removeClass('alert-success').addClass('alert-warning');

                            }

                        },
                        error: function (request, status, error) {

                            notifyWarning("Erreur lors de l'enregistrement");
                        }

                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }
            });
        });
    });


    //Suppression d'autre risque
    $(document).on('click', ".btn_supprimer_autrerisque", function () {

        let police_id = $(this).data('police_id');
        let autresrisque_id = $(this).data('autresrisque_id');
        let href = $(this).data('href');
        //alert(href);
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cet autre risque ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { police_id: police_id, autresrisque_id: autresrisque_id },
                            success: function (e) {
                                notifySuccess("autrerisque non trouvée !");
                                location.reload();
                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression de la autrerisque');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });

    });


    //DETAILS de l'historique d'autres risques
    $(document).on("click", ".btn_details_histo_autrerisque", function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-details_autrerisque_histo .dataTable:not(.customDataTable_)').DataTable({
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"
                },
                order: [[0, 'desc']],
                lengthMenu: [
                    [100],
                    [100],
                ],
                searching: false,
                lengthChange: false,
            });

            let i = 0;
            $('.dropzone_area').each(function (myElement) {
                let zone_id = $(this).attr('id');
                let href = $(this).attr('action');

                let dropzone = new Dropzone("#" + zone_id, { url: href, dictDefaultMessage: "" });

            });

            $('#modal-details_autrerisque_histo').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-details_autrerisque_histo').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-details_autrerisque_histo').modal();

        });
    });


    //ajout d'un avenant sur une police
    $("#btn_save_avenant").on('click', function () {

        let formulaire = $('#form_add_avenant');
        let href = formulaire.attr('action');
        let href_police = $(this).attr('data-href_police');
        let mouvement = $('#mouvement').val();

        console.log('href_police', href_police);

        if (formulaire.valid()) {

            $.ajax({
                type: 'post',
                url: href,
                data: formulaire.serialize(),
                success: function (response) {

                    if (response.statut == 1) {

                        //Vider le formulaire
                        resetFields('#' + formulaire.attr('id'));
                        console.log(mouvement);
                        console.log(typeof(mouvement));
                        if(mouvement === '5' || mouvement === '16'){
                            helper_modification_police(href_police)
                        }else{
                             notifySuccess(response.message, function () {
                                location.reload();
                            });
                        }

                    } else {

                        let errors = JSON.parse(JSON.stringify(response.errors));
                        let errors_list_to_display = '';
                        for (field in errors) {
                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                        }

                        $('#modal-avenant .alert .message').html(errors_list_to_display);

                        $('#modal-avenant .alert ').fadeTo(2000, 500).slideUp(500, function () {
                            $(this).slideUp(500);
                        }).removeClass('alert-success').addClass('alert-warning');

                    }

                },
                error: function (request, status, error) {

                    notifyWarning("Erreur lors de l'enregistrement");
                }

            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner tous les champs obligatoires');
        }


    });


    //Changement de mouvement, charger les motifs liés
    $('#mouvement').on('change', function () {

        let mouvement_id = $(this).val();
        let police_id = $('#police_id').val();

        $('#motif').html('<option value="">---------------------------</option>');

        $.ajax({
            type: 'get',
            url: '/production/mouvement/' + police_id + '/' + mouvement_id + '/motifs',
            success: function (motifs) {

                $('#motif').html('').append('<option value="">Sélectionnez un motif</option>');

                motifs.forEach(function (motif) {
                    $('#motif').append('<option value="' + motif.pk + '">' + motif.fields.libelle + '</option>');
                });

            },
            error: function () { }
        });

        //
        if (mouvement_id == 5) {
            $('#box_date_fin_periode_garantie').show();
            $('#date_fin_periode_garantie').attr('required', 'true');
        } else {
            $('#box_date_fin_periode_garantie').hide();
            $('#date_fin_periode_garantie').removeAttr('required');
        }


    });

    //fin ajout d'un avenant sur une police


    //ajout d'un avenant sur le sinistre
    $("#btn_save_avenant_sinistre").on('click', function () {

        let formulaire = $('#form_add_avenant_sinistre');
        let href = formulaire.attr('action');
        let href_sinistre = $(this).attr('data-href_sinistre');
        let mouvement = $('#mouvement_sinistre').val();

        if (formulaire.valid()) {

            $.ajax({
                type: 'post',
                url: href,
                data: formulaire.serialize(),
                success: function (response) {

                    if (response.statut == 1) {

                        //Vider le formulaire
                        resetFields('#' + formulaire.attr('id'));
                        console.log(mouvement);
                        console.log(typeof(mouvement));
                        if (mouvement >= 18 && mouvement <= 32) {
                            helper_modification_sinistre(href_sinistre)
                        }else{
                            notifySuccess(response.message, function () {
                                location.reload();
                            });
                        }

                    } else {

                        let errors = JSON.parse(JSON.stringify(response.errors));
                        let errors_list_to_display = '';
                        for (field in errors) {
                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                        }

                        $('#modal-avenant_sinistre .alert .message').html(errors_list_to_display);

                        $('#modal-avenant_sinistre .alert ').fadeTo(2000, 500).slideUp(500, function () {
                            $(this).slideUp(500);
                        }).removeClass('alert-success').addClass('alert-warning');

                    }

                },
                error: function (request, status, error) {

                    notifyWarning("Erreur lors de l'enregistrement");
                }

            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner tous les champs obligatoires');
        }

    });


    //Changement de mouvement, charger les motifs liés
    $('#mouvement_sinistre').on('change', function () {

        $('#btn_save_avenant_sinistre').prop('disabled', true);

        let mouvement_id = $(this).val();
        let sinistre_id = $('#sinistre_id').val();

        $.ajax({
            type: 'get',
            url: '/production/sinsitre/' + sinistre_id + '/' + mouvement_id + '/etapes',
            success: function (response) {
                if (response.statut != 0) {
                    $('#btn_save_avenant_sinistre').prop('disabled', false);
                } else {
                    $('#btn_save_avenant_sinistre').prop('disabled', true);
                    notifyWarning(response.message, function () {});
                }
            },
            error: function () {
                console.error("Erreur lors de la requête AJAX");
                $('#btn_save_avenant_sinistre').prop('disabled', false);
            }
        });

        let selectedOption = $(this).find(':selected');
        let mouvement_nom = selectedOption.data('movement_nom');

        $('#modal-modification_sinistre #titre_mouvement').text(mouvement_nom);

        //
        if (mouvement_id == 33) {
            $('#box_date_cloture_sinistre').show();
            $('#date_cloture_sinistre').attr('required', 'true');
        } else {
            $('#box_date_cloture_sinistre').hide();
            $('#date_cloture_sinistre').removeAttr('required');
        }

    });

    //fin ajout d'un avenant sur un sinistre


    //Added on 10102023: ajout d'un bouton pour afficher la zone de modification de l'affection

    $(document).on('click', '#btn_show_form_update_affection', function () {
        $('#form_Add_affection_hopit').show();
        $(this).hide();
    });

    //showing selon choix type prefinancement
    $(document).on('change', '#option_mode_prefinancement, #option_mode_prefinancement_update', function () {

        $('.if_tpp').addClass("d-none");
        $('.if_tpp .form-control').removeAttr('required');

        let option_mode_prefinancement = $(this).val();

        switch (option_mode_prefinancement) {
            case "TPP"://prime par famille
                $('.if_tpp').removeClass("d-none");
                $('.if_tpp .form-control').attr('required', 'required');
                break;
        }

    });

    //showing selon choix type prefinancement
    $(document).on('change', '#formule_rubriques, #formule_rubriques_update', function () {

        $(".select2-selection__choice__display").css("color", "#000");

    });

    $(document).on('click', '#btnAddAffectionToDossierSinistre', function () {
        let formulaire = $('#form_Add_affection_hopit');
        let href = formulaire.attr('action');
        $.ajax({
            type: 'post',
            url: href,
            data: formulaire.serialize(),
            success: function (response) {

                if (response.statut == 1) {
                    notifySuccess(response.message, function () {
                        location.reload();
                    });

                } else {
                    notifySuccess(response.message);
                }

            },
            error: function (request, status, error) {

                notifyWarning("Erreur lors de l'ajout de l'affection");
            }

        });
    })

    $("#execution_requete_excel").on('click', function () {
        let btn_valider = $(this);

        let formulaire = $('#form_execution_requete_excel');
        let href = formulaire.attr('action');
        let taskVerifUrl = formulaire.attr('data-task-url');
        //alert(taskVerifUrl);

        if (formulaire.valid()) {

            btn_valider.hide();
            $('#loader').show();

            $.ajax({
                type: 'post',
                url: href,
                data: formulaire.serialize(),
                cache: false,
                xhr: function () {
                    var xhr = new XMLHttpRequest();
                    xhr.onreadystatechange = function () {
                        if (xhr.readyState == 2) {
                            if (xhr.status == 200) {
                                xhr.responseType = "blob";
                            } else {
                                xhr.responseType = "json";
                            }
                        }
                    };
                    return xhr;
                },
                success: function (data) {
                    // SUIVI SP CLIENT PAR FILIALE
                    fileName = $('select[name="query_name"]').val() + ".xlsx";
                    //Convert the Byte Data to BLOB object.
                    var blob = new Blob([data], { type: "application/octetstream" });

                    //Check the Browser type and download the File.
                    var isIE = false || !!document.documentMode;
                    if (isIE) {
                        window.navigator.msSaveBlob(blob, fileName);
                    } else {
                        var url = window.URL || window.webkitURL;
                        link = url.createObjectURL(blob);
                        var a = $("<a />");
                        a.attr("download", fileName);
                        a.attr("href", link);
                        $("body").append(a);
                        a[0].click();
                        $("body").remove(a);
                    }

                    btn_valider.show();
                    $('#loader').hide();

                    // Background query task delect
                    $.ajax({ type: 'post', url: taskVerifUrl, data: {} });


                },
                error: function (response) {
                    console.log(response);
                    btn_valider.show();
                    $('#loader').hide();

                    notifyWarning("Votre requête a dépassé le temps limite d'exécution. Nous la traitons en arrière-plan et vous notifierons dès que celle-ci sera terminée. Merci pour votre patience.");

                }
            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner tous les champs obligatoires');
        }

    });

    $("#execution_requete_super_admin").on('click', function () {
        let btn_valider = $(this);

        let formulaire = $('#form_execution_requete_super_admin');
        let href = formulaire.attr('action');

        if (formulaire.valid()) {

            btn_valider.hide();
            $('#loader').show();
            $('#msg-box').html("");

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment effectuer l'action ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formulaire.serialize(),
                                success: function (data) {
                                    console.log('success',data);
                                    btn_valider.show();
                                    $('#loader').hide();
                                    $('#msg-box').html(data.message);
                                },
                                error: function (response) {
                                    console.log('error', response);
                                    btn_valider.show();
                                    $('#loader').hide();
                                    $('#msg-box').html(response.responseJSON.message);

                                }
                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();
                            btn_valider.show();
                            $('#loader').hide();

                        }
                    }
                ]
            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });
        }

    });

    $("#execution_requete_excel_compta").on('click', function () {
        let btn_valider = $(this);

        let formulaire = $('#form_execution_requete_excel_compta');
        let href = formulaire.attr('action');

        if (formulaire.valid()) {

            btn_valider.hide();
            $('#loader_compta').show();

            $.ajax({
                type: 'post',
                url: href,
                data: formulaire.serialize(),
                cache: false,
                xhr: function () {
                    var xhr = new XMLHttpRequest();
                    xhr.onreadystatechange = function () {
                        if (xhr.readyState == 2) {
                            if (xhr.status == 200) {
                                xhr.responseType = "blob";
                            } else {
                                xhr.responseType = "json";
                            }
                        }
                    };
                    return xhr;
                },
                success: function (data) {
                    fileName = $('select[name="query_name"]').val() + ".xlsx";
                    //Convert the Byte Data to BLOB object.
                    var blob = new Blob([data], { type: "application/octetstream" });

                    //Check the Browser type and download the File.
                    var isIE = false || !!document.documentMode;
                    if (isIE) {
                        window.navigator.msSaveBlob(blob, fileName);
                    } else {
                        var url = window.URL || window.webkitURL;
                        link = url.createObjectURL(blob);
                        var a = $("<a />");
                        a.attr("download", fileName);
                        a.attr("href", link);
                        $("body").append(a);
                        a[0].click();
                        $("body").remove(a);
                    }

                    btn_valider.show();
                    $('#loader_compta').hide();

                },
                error: function (response) {
                    console.log(response);
                    btn_valider.show();
                    $('#loader_compta').hide();
                    notifyWarning("Une erreur c'est produite lors de l'execution de la requête");

                }
            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner tous les champs obligatoires');
        }

    });

    //fin


    //Standard: ouvrir les popups de modification
    $(".btn_open_on_modal").on('click', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#modal-dynamique').find('.modal-title').text(modal_title);
        $('#modal-dynamique').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
        $('#modal-dynamique').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

        $('#modal-dynamique').modal({ backdrop: "static ", keyboard: false }).find('.modal-body').text("Chargement en cours...").load(href, function () {
            alert('Data loaded ');
        });

    });

    //Valider les modifications
    $("#btn_valider").on('click', function () {

        let model_name = $(this).attr('data-model_name');
        let href = $(this).attr('data-href');
        let formulaire = $('#modal-dynamique').find('form');

        switch (model_name) {

            default:

                $.ajax({
                    url: href,
                    type: 'post',
                    data: formulaire.serialize(),
                    success: function (response) {

                        if (response.statut == 1) {

                            $('#modal-dynamique .alert .message').text(response.message);

                            $('#modal-dynamique .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                $(this).slideUp(500);
                                $("#modal-dynamique").modal('toggle');

                                notifySuccess(response.message);
                                location.reload();

                            }).removeClass('alert-warning').addClass('alert-success');

                        } else {

                            $('#modal-dynamique .alert .message').text(response.message);

                            $('#modal-dynamique .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                $(this).slideUp(500);
                            }).removeClass('alert-success').addClass('alert-warning');

                        }

                    },
                    error: function () {
                        notifyWarning('Erreur lors de la modification');
                    }
                });

                break;

        }

    });



    //*************** AJOUT ET MODIFICATION DE POLICE *****************//

    //ajout d'une police
    function isValidDate(dateStr) {
        return dateStr && !isNaN(Date.parse(dateStr));
    }

    function manageModeRenouvellement() {
        let modeRenouvellement = $('#mode_renouvellement').val();
        let dateDebutPoliceInput = $('#date_debut_effet');
        let dateFinPoliceInput = $('#date_fin_police');
        let dateFinPoliceLabelStar = $('#label_date_fin_police .required');
        let fractionnementSelect = $('select[name="fractionnement"]');
        let fractionnement_hint = $('#fractionnement_hint');

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
        let dateDebut = $('#date_debut_effet').val();
        let dateFinEffet = $('#date_fin_effet').val();
        let dateFinPolice = $('#date_fin_police').val();
        let mode = $('#mode_renouvellement').val();
        let btnSubmit = $('#btn_save_police');

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
    $(document).on('change', "#mode_renouvellement, #date_fin_effet, #date_fin_police", function () {
        manageModeRenouvellement();
        validateDates();
    });



    // Fonction pour gérer l'affichage et la validation des champs
    function gererApporteurChamps() {
        if ($('#yes_apporteur').is(':checked')) {
            $('.apporteur-champs').show();
            $('.intermediaire_champ_obligatoire').attr('required', true);
        } else {
            $('.apporteur-champs').hide();
            $('.intermediaire_champ_obligatoire').removeAttr('required');
        }
    }

    // Appel initial pour gérer l'affichage
    gererApporteurChamps();

    // Gestionnaire d'événement pour les changements de radio
    $('input[name="apporteur"]').change(function() {
        gererApporteurChamps();
    });



    // Gestion de la soumission du formulaire
    $("#btn_save_police").on('click', function (e) {
        let btn_submit = $(this);

        // Vérifier les dates avant de désactiver le bouton
        if (!validateDates()) {
            return;
        }

        let isValid = true;

        // Validation des champs obligatoires dans les onglets "General", "Facturation" et "Garantie"
        $('#general-tab, #facturation-tab, #garantie-tab').each(function () {
            let tabId = $(this).attr('href');
            $(tabId).find('input[required], select[required]').each(function () {
                if (!$(this).val()) {
                    $(this).addClass('is-invalid');
                    isValid = false;
                } else {
                    $(this).removeClass('is-invalid');
                }
            });
        });

        // Gestion des champs intermediaires selon apporteur
        if ($('#yes_apporteur').is(':checked')) {
            console.log('avec apporteur');
            $('.intermediaire_champ_obligatoire').each(function () {
                $(this).attr('required', true);
                if (!$(this).val()) {
                    $(this).addClass('is-invalid');
                    isValid = false;
                } else {
                    $(this).removeClass('is-invalid');
                }
            });
        } else {
            console.log('sans apporteur');
            $('.intermediaire_champ_obligatoire').each(function () {
                $(this).removeAttr('required');
                $(this).removeClass('is-invalid');
            });
        }


        // Validation des champs obligatoires dynamiques
        if ($('#vehicule-tab').is(':visible')) {
            $('.vehicule_champ_obligatoire').each(function () {
                if (!$(this).val()) {
                    isValid = false;
                    $(this).addClass('is-invalid');
                } else {
                    $(this).removeClass('is-invalid');
                }
            });
        }

        if ($('#marchandise-tab').is(':visible')) {
            $('.marchandise_champ_obligatoire').each(function () {
                if (!$(this).val()) {
                    isValid = false;
                    $(this).addClass('is-invalid');
                } else {
                    $(this).removeClass('is-invalid');
                }
            });
        }

        if (!isValid) {
            e.preventDefault(); // Empêcher la soumission
            notifyWarning('Veuillez renseigner tous les champs obligatoires.');
            return;
        }

        btn_submit.attr('disabled', true);

        let formulaire = $('#form_add_police');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();
        let files = $('#form_add_police #fichier_contrat')[0].files;
        console.log('files : ', files);
        if (formulaire.valid()) {

            if (files.length > 0) {
                formData.append('fichier_contrat', files[0]);
            }

            let data_serialized = formulaire.serialize();
            $.each(data_serialized.split('&'), function (index, elem) {
                let vals = elem.split('=');
                let key = vals[0];
                let valeur = decodeURIComponent(vals[1].replace(/\+/g, ' '));
                formData.append(key, valeur);
            });

            $.ajax({
                type: 'post',
                url: href,
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    btn_submit.removeAttr('disabled');

                    if (response.statut == 1) {
                        let police = response.data;

                        // Vider le formulaire
                        resetFields('#' + formulaire.attr('id'));
                        resetFields('#form_add_autres_taxes');
                        $("#form_add_police select").each(function () {
                            $(this).prop('selectedIndex', 0).trigger('change');
                        });

                        // Vider les cookies enregistrées
                        document.cookie = "taxes=";

                        notifySuccess(response.message, function () {
                            location.reload();
                        });

                    } else {
                        let errors = JSON.parse(JSON.stringify(response.errors));
                        let errors_list_to_display = '';
                        for (let field in errors) {
                            errors_list_to_display += '- ' + field.charAt(0).toUpperCase() + field.slice(1) + ' : ' + errors[field] + '<br/>';
                        }

                        $('#modal-police .alert .message').html(errors_list_to_display);
                        $('#modal-police .alert').fadeTo(2000, 500).slideUp(500).removeClass('alert-success').addClass('alert-warning');
                    }
                },
                error: function () {
                    btn_submit.removeAttr('disabled');
                    notifyWarning("Erreur lors de l'enregistrement ");
                }
            });

        } else {
            btn_submit.removeAttr('disabled');

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();
            $.each(validator.errorMap, function (index, value) {
                console.log('Id: ' + index + ' Message: ' + value);
            });

            notifyWarning('Veuillez renseigner tous les champs obligatoires');
        }
    });


    //actualiser le taux de commission au changement de la compagnie
    $("#modal-police #branche").on('change', function () {

        let branche_id = $(this).val();
        let branche_code = $(this).find('option:selected').data('branche_code');

        $.ajax({
            type: 'get',
            url: '/production/ajax_produits/' + branche_id,
            dataType: 'json',
            success: function (produits) {
                $('#modal-police #produit').html('').append('<option value="">Choisir un produit</option>');

                produits.forEach(function (produit) {
                    $('#modal-police #produit').append('<option value="' + produit.pk + '">' + produit.fields.nom + '</option>');
                });
            },
            error: function () {
                console.log('Erreur loading produits ');
            }
        });
    });

    //actualiser la liste des apporteurs
    $("#btn_refresh_liste_apporteurs").on('click', function () {
        //alert("btn_refresh_liste_apporteurs");

        let href_apporteurs = $(this).data('href');

        $.ajax({
            type: 'get',
            url: href_apporteurs,
            dataType: 'json',
            success: function (apporteurs) {
                $('#modal-police .intermediaire').each(function () {
                    var $intermediaire = $(this);
                    if ($intermediaire.val() === "") {
                        $intermediaire.html('').append('<option value="">Choisir</option>');
                    }
                });

                apporteurs.forEach(function (apporteur) {
                    $('#modal-police .intermediaire').each(function () {
                        var $intermediaire = $(this);
                        if ($intermediaire.val() === "") {
                            $intermediaire.append('<option value="' + apporteur.pk + '">' + apporteur.fields.nom + ' ' + apporteur.fields.prenoms + '</option>');
                        }
                    });
                });
            },
            error: function () {
                console.log('Erreur de chargement des apporteurs ');
            }
        });

    });

    //fin ajout d'un police sur une police


    //TODO:modification de police
    // Créer une function
    function helper_modification_police(href, modal_title, model_name) {
        $('#olea_std_dialog_box').load(href, function () {
            const $modal = $('#modal-modification_police');
            const $btnSave = $("#btn_save_modification_police");
            const formulaire = $('#form_update_police');

            // 1. Fonction de validation des dates déclarée ici, disponible pour tout le scope
            function validateDatesModification() {
                const police_date_debut   = $modal.find('#modification_date_debut_effet').val();
                const police_date_fin     = $modal.find('#modification_date_fin_effet').val();
                const police_date_fin_police = $modal.find('#modification_date_fin_police').val();
                const mode_renouvellement = $modal.find('#modification_mode_renouvellement').val();

                // Réactiver le bouton au départ
                $btnSave.prop('disabled', false);

                if (isValidDate(police_date_debut)) {
                    if (mode_renouvellement === "Tacite Reconduction" && isValidDate(police_date_fin)) {
                        if (new Date(police_date_debut) >= new Date(police_date_fin)) {
                            notifyWarning("La date de renouvellement doit être strictement postérieure à la date de début.");
                            $btnSave.prop('disabled', true);
                            return false;
                        }
                    } else if (mode_renouvellement === "Sans Tacite Reconduction" && isValidDate(police_date_fin_police)) {
                        if (new Date(police_date_debut) >= new Date(police_date_fin_police)) {
                            notifyWarning("La date de fin du contrat doit être strictement postérieure à la date de début.");
                            $btnSave.prop('disabled', true);
                            return false;
                        }
                    }
                }
                return true;
            }

            // 2. Appliquer le mask, titre, classes, etc.
            AppliquerMaskSaisie();
            $modal
                .attr({ 'data-backdrop': 'static', 'data-keyboard': false })
                .find('.modal-title').text(modal_title).end()
                .find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href }).end()
                .find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');
            $modal.modal();
            $('#option_calcul_prime_modification').change();

            // 3. Lier validateDatesModification aux changements des champs concernés
            $modal.on('change', '#date_debut_effet, #date_fin_effet, #date_fin_police, #mode_renouvellement',
                validateDatesModification
            );

            // 4. Gestion du clic “Valider”
            $btnSave.off('click').on('click', function (e) {
                e.preventDefault();

                // Appel de la validation de dates
                if (!validateDatesModification()) {
                    return;
                }

                // Validation des champs obligatoires
                let isValid = true;
                $('#general-tab_modification, #facturation-tab_modification, #garantie-tab_modification').each(function () {
                    const tabPane = $($(this).attr('href'));
                    tabPane.find('input[required], select[required]').each(function () {
                        if (!this.value) {
                            $(this).addClass('is-invalid');
                            isValid = false;
                        } else {
                            $(this).removeClass('is-invalid');
                        }
                    });
                });
                // validations dynamiques
                if ($('#vehicule-tab_modification').is(':visible')) {
                    $('.vehicule_champ_obligatoire_modification').each(function () {
                        $(this).val() ? $(this).removeClass('is-invalid') : ($(this).addClass('is-invalid'), isValid = false);
                    });
                }
                if ($('#marchandise-tab_modification').is(':visible')) {
                    $('.marchandise_champ_obligatoire_modification').each(function () {
                        $(this).val() ? $(this).removeClass('is-invalid') : ($(this).addClass('is-invalid'), isValid = false);
                    });
                }

                if (!isValid) {
                    notifyWarning('Veuillez renseigner tous les champs obligatoires.');
                    return;
                }

                // forcer validation de tous les champs même cachés
                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();
                let files = $('#form_update_police #fichier_contrat')[0].files;

                // Confirmation Noty
                noty({
                    text: 'Voulez-vous vraiment modifier cette police ?',
                    type: 'warning',
                    layout: 'center',
                    theme: 'defaultTheme',
                    buttons: [
                        {
                            addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                $noty.close();

                                // This is the key change: only append the file if it exists.
                                if (files.length > 0 && files[0]) {
                                    formData.append('fichier_contrat', files[0], files[0].name);
                                }

                                formulaire.serializeArray().forEach(({ name, value }) => {
                                    formData.append(name, value);
                                });

                                // Requête AJAX
                                $.ajax({
                                    type: 'POST',
                                    url: formulaire.attr('action'),
                                    data: formData,
                                    processData: false,
                                    contentType: false,
                                    xhrFields: { withCredentials: true },
                                    success(response) {
                                        if (response.statut == 1) {
                                            notifySuccess(response.message, () => location.reload());
                                        } else if (response.statut == 0) {
                                            notifyWarning(response.message);
                                        } else {
                                            let errors = response.errors || {};
                                            let html = Object.entries(errors)
                                                .map(([f, msg]) => `- ${ucfirst(f)} : ${msg}<br/>`)
                                                .join('');
                                            $modal.find('.alert .message').html(html);
                                            $modal.find('.alert')
                                                .fadeTo(2000, 500)
                                                .slideUp(500, function () { $(this).slideUp(500); })
                                                .removeClass('alert-success')
                                                .addClass('alert-warning');
                                        }
                                    },
                                    error() {
                                        notifyWarning("Erreur lors de l'enregistrement");
                                    }
                                });
                            }
                        },
                        {
                            addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                $noty.close();
                            }
                        }
                    ]
                });
            });
        });
    }
    //fin modification de police

    $("#modal-police #compagnie, #modal-police #produit").on('change', function () {

        let compagnie_id = $("#modal-police #compagnie").val();
        let produit_id = $('#modal-police #produit').val();

        // Réinitialiser les champs si l'un des sélecteurs est modifié
        $('#modal-police #taux_com_courtage').val('');
        $('#modal-police #taux_com_courtage_terme').val('');

        if (compagnie_id && produit_id) {
            $.ajax({
                type: 'get',
                url: '/production/compagnie/ajax_infos_compagnie/' + compagnie_id + '/' + produit_id,
                dataType: 'json',
                success: function (data) {

                    let taux_com_courtage = parseFloat(data.taux_com_courtage);
                    let taux_com_courtage_terme = parseFloat(data.taux_com_courtage_terme);

                    console.log('taux_com_courtage : ', taux_com_courtage);
                    console.log('taux_com_courtage_terme : ', taux_com_courtage_terme);

                    $('#modal-police #taux_com_courtage').val(taux_com_courtage);
                    $('#modal-police #taux_com_courtage_terme').val(taux_com_courtage_terme);

                    calculer_montant_divers_police();
                },
                error: function () {
                    console.log('Erreur de chargement : ajax_infos_compagnie ');
                }
            });
        }

    });

    //
    $(document).on("keyup change", "#modal-police .calculs_handler_police", function (event) {

        if (event.which == 13) {
            event.preventDefault();
        }

        calculer_montant_divers_police();

    });

    function calculer_montant_divers_police() {

        let prime_ht = parseInt($('#modal-police #prime_ht').val().replaceAll(' ', ''));
        let cout_police_compagnie = parseInt($('#modal-police #cout_police_compagnie').val().replaceAll(' ', ''));
        let cout_police_courtier = parseInt($('#modal-police #cout_police_courtier').val().replaceAll(' ', ''));
        let taxe = parseInt($('#modal-police #taxe').val().replaceAll(' ', ''));
        let autres_taxes = parseInt($('#modal-police #autres_taxes').val().replaceAll(' ', ''));

        let taux_com_gestion = parseFloat($('#modal-police #taux_com_gestion').val());
        let taux_com_courtage = parseFloat($('#modal-police #taux_com_courtage').val());
        let taux_com_courtage_terme = parseFloat($('#modal-police #taux_com_courtage_terme').val());

        if (isNaN(prime_ht)) { prime_ht = 0; }
        if (isNaN(cout_police_compagnie)) { cout_police_compagnie = 0; }
        if (isNaN(cout_police_courtier)) { cout_police_courtier = 0; }
        if (isNaN(taxe)) { taxe = 0; }
        if (isNaN(autres_taxes)) { autres_taxes = 0; }
        if (isNaN(taux_com_gestion)) { taux_com_gestion = 0; }
        if (isNaN(taux_com_courtage)) { taux_com_courtage = 0; }
        if (isNaN(taux_com_courtage_terme)) { taux_com_courtage_terme = 0; }

        let prime_ttc = prime_ht + cout_police_compagnie + cout_police_courtier + taxe + autres_taxes;

        console.log('prime_ht', prime_ht);
        console.log('cout_police_compagnie', cout_police_compagnie);
        console.log('cout_police_courtier', cout_police_courtier);
        console.log('taxe', taxe);
        console.log('autres_taxes', autres_taxes);
        console.log('taux_com_gestion', taux_com_gestion);
        console.log('taux_com_courtage', taux_com_courtage);
        console.log('taux_com_courtage_terme', taux_com_courtage_terme);
        console.log('prime_ttc', prime_ttc);


        let montant_commission_gestion = (taux_com_gestion / 100) * prime_ht;
        let montant_commission_courtage = (taux_com_courtage / 100) * prime_ht;


        let total_taux_com_affaire_nouvelle = 0;
        let total_taux_com_renouvelement = 0;
        let montant_commission_intermediaire = 0;
        let total_montant_commission_intermediaire = 0;

        $('.taux_com_affaire_nouvelle').each(function () {

            let taux_com_affaire_nouvelle = parseFloat($(this).val());
            let taux_com_renouvelement = parseFloat($(this).closest('tr').find('.taux_com_renouvelement').val());
            let base_calcul_taux_retrocession = $(this).closest('tr').find('.base_calcul_taux_retrocession').val();
            let intermediaire = $(this).closest('tr').find('.intermediaire').val();

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

        $('#modal-police #prime_ttc').val(prime_ttc);

        $('#modal-police #commission_courtage').val(montant_commission_courtage);

        $('#modal-police #commission_gestion').val(montant_commission_gestion);

        $('#modal-police #total_commission_intermediaire').val(total_montant_commission_intermediaire);


    }

    //Pour la création de police
    function on_change_participation(participation) {

        if (participation == 'OUI') {

            $('#modal-police #box_taux_participation').show();

            $("#modal-police #taux_participation").attr('required', true);

            $('#modal-police #box_taux_participation').find('label').html('Taux de participation <span class="text-red">*</span>');

        } else {

            $('#modal-police #box_taux_participation').hide();

            $("#modal-police #taux_participation").val('0').removeAttr('required');

            $('#modal-police #box_taux_participation').find('label').html('Taux de participation ');

        }

    }

    //on_change_participation();
    $(document).on("change", "#modal-police .participation", function () {

        let participation = $(this).val();

        on_change_participation(participation);

    });


    function appendToStorage(name, data) {
        let old = localStorage.getItem(name);
        try {
            old = JSON.parse(old);
        } catch (e) {
            old = [];
        }
        localStorage.setItem(name, JSON.stringify(old.concat(data)));
    }

    $(document).on("keyup", "#form_add_autres_taxes .montant_taxe", function () {

        if (event.which == 13) {
            event.preventDefault();
        }

        let montant_total_autres_taxes = parseInt(0);

        $("#modal-autres_taxes .montant_taxe").each(function (index, element) {

            //element = this
            let montant = parseInt($(element).val().replaceAll(' ', ''));
            montant = (montant != '') ? montant : parseInt(0);

            if (isNaN(montant)) {
                montant = parseInt(0);
            }

            //console.log('montant: '+ isNaN(montant));

            montant_total_autres_taxes += montant;

        });

        //console.log('total: '+montant_total_autres_taxes);

        $('#modal-police #autres_taxes').val(montant_total_autres_taxes);
        $('#modal-autres_taxes .total_autres_taxes').text(montant_total_autres_taxes);

        calculer_montant_divers_police();

    });


    $('#modal-apporteurs').on('show.bs.modal', function (e) {
        $(this).find('table').css({ width: '100%' });

        let intermediaire = $(e.relatedTarget).closest('tr').find('.intermediaire:first');
        let intermediaire_nom_prenoms = $(e.relatedTarget).closest('tr').find('.intermediaire_nom_prenoms:first');

        $('.selected_field_intermediaire_id').removeClass('selected_field_intermediaire_id');
        $('.selected_field_intermediaire_nom_prenoms').removeClass('selected_field_intermediaire_nom_prenoms');

        intermediaire.addClass('selected_field_intermediaire_id');
        intermediaire_nom_prenoms.addClass('selected_field_intermediaire_nom_prenoms');

        $(document).on("click", "#modal-apporteurs .btnSetSelectedApporteur", function () {

            let selected_apporteur_id = $(this).data('apporteur_id');
            let selected_apporteur_nom_prenoms = $(this).data('apporteur_nom_prenoms');


            $('.selected_field_intermediaire_id').val(selected_apporteur_id);
            $('.selected_field_intermediaire_nom_prenoms').val(selected_apporteur_nom_prenoms);

            calculer_montant_divers_police();

        });

        //init datatables
        if (!$.fn.DataTable.isDataTable('#table_apporteurs')) {

            $('#table_apporteurs').DataTable({
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"
                },
                order: [[0, 'desc']],
                lengthMenu: [
                    [5, 10],
                    [5, 10],
                ],
                //scrollY: '100px',
                //scrollX: true,
                //scrollCollapse: false,
                paging: true,
                processing: false,
                serverSide: false,
                fnDrawCallback: function (oSettings) {
                    //$(".radio_apporteur").prop('checked', false);//décocher les radios
                    //$(this).css({width:'100%', display: 'inline-block'});
                }
            });

        }

    });

    //A la fermeture de la fenetre des autres taxes, sauvegarder les données dans les cookies pour pouvoir les récupérer coté serveur
    $('#modal-autres_taxes').on('hidden.bs.modal', function () {
        $('body').addClass('modal-open');

        //Enregistrer les autres taxes saisies

        if (typeof (Storage) !== "undefined") {

            localStorage.setItem('taxes', "");

            // Code for localStorage
            $("#modal-autres_taxes .montant_taxe").each(function (index, element) {

                //element = this
                let taxe_id = $(element).attr('data-taxe_id');
                let montant = parseInt($(element).val().replaceAll(' ', ''));
                montant = (montant != '') ? montant : parseInt(0);

                if (isNaN(montant)) {
                    montant = parseInt(0);
                }

                let taxe = {
                    id: taxe_id,
                    montant: montant,
                }

                appendToStorage('taxes', taxe);

            });

            let taxes_result = localStorage.getItem('taxes');

            console.log(taxes_result);

            //enregistrer dans le cookies pour l'utiliser coté serveur avec python
            document.cookie = "taxes=" + taxes_result;


        } else {
            notifyWarning('No web storage Support.');
        }

    });

    //Insertion ligne supplémantaire dans l'onglet INTERMEDIAIRES/APPORTAUERS - lors de l'ajout de police
    $(document).on("click", "#table_apporteurs_police #btnAddLigneApporteur", function () {
        let tr = $('#table_apporteurs_police tbody tr:first');

        let timestamp = Date.now();

        $('#table_apporteurs_police tbody tr:last')
            .after('<tr id="tr_' + timestamp + '">' + tr.html() + '</tr>')
            .ready(function () {
                AppliquerMaskSaisie();
            });
    });

    //
    $(document).on("click", ".btnSupprimerLigneApporteur", function () {
        let nombre_ligne = $('#table_apporteurs_police tbody tr').length;

        if (nombre_ligne > 1) {
            $(this).parent().parent().remove();

            //recalculer les primes divers
            calculer_montant_divers_police();

        } else {
            let tr_ligne_id = $('#table_apporteurs_police tbody tr').attr('id');
            resetFields('#' + tr_ligne_id);
            //notifyWarning('Au moins une ligne doit être conservée')
        }

    });


    //FIN Insertion ligne supplémantaire dans l'onglet INTERMEDIAIRES/APPORTAUERS - lors de l'ajout de police

    //Insertion ligne supplémantaire dans l'onglet INTERMEDIAIRES/APPORTAUERS - lors de la modification de police
    $(document).on("click", "#table_apporteurs_police_modification #btnAddLigneApporteur_modification", function () {
        let tr = $('#table_apporteurs_police_modification tbody tr:first');

        let timestamp = Date.now();

        $('#table_apporteurs_police_modification tbody tr:last')
            .after('<tr id="tr_' + timestamp + '">' + tr.html() + '</tr>')
            .ready(function () {
                AppliquerMaskSaisie();
            });
    });

    //
    $(document).on("click", "#table_apporteurs_police_modification .btnSupprimerLigneApporteur_modification", function () {
        let nombre_ligne = $('#table_apporteurs_police_modification tbody tr').length;

        if (nombre_ligne > 1) {
            $(this).parent().parent().remove();

            //recalculer les primes divers
            calculer_montant_divers_police_modification();

        } else {
            //notifyWarning('Au moins une ligne doit être conservée')
        }

    });


    //FIN Insertion ligne supplémantaire dans l'onglet INTERMEDIAIRES/APPORTAUERS - lors de la modification de police

    //GESTION MODIFICATION AUTRES TAXES
    $(document).on("keyup", "#form_add_autres_taxes_modification .montant_taxe", function (event) {

        if (event.which == 13) {
            event.preventDefault();
        }

        let montant_total_autres_taxes = parseInt(0);

        $("#modal-autres_taxes_modification .montant_taxe").each(function (index, element) {

            //element = this
            let montant = parseInt($(element).val().replaceAll(' ', ''));
            montant = (montant != '') ? montant : parseInt(0);

            if (isNaN(montant)) {
                montant = parseInt(0);
            }

            montant_total_autres_taxes += montant;

        });

        //console.log('total: '+montant_total_autres_taxes);

        $('#modal-modification_police #autres_taxes_modification').val(montant_total_autres_taxes);
        $('#modal-autres_taxes_modification .total_autres_taxes_modification').text(montant_total_autres_taxes);

        calculer_montant_divers_police_modification();

    });


    //A la fermeture de la fenetre des autres taxes, sauvegarder les données dans les cookies pour pouvoir les récupérer coté serveur
    $(document).on("hidden.bs.modal", "#modal-autres_taxes_modification", function () {
        $('body').addClass('modal-open');

        //Enregistrer les autres taxes saisies

        if (typeof (Storage) !== "undefined") {

            localStorage.setItem('taxes_modification', "");

            // Code for localStorage
            $("#modal-autres_taxes_modification .montant_taxe").each(function (index, element) {

                //element = this
                let taxe_id = $(element).attr('data-taxe_id');
                let montant = parseInt($(element).val().replaceAll(' ', ''));
                montant = (montant != '') ? montant : parseInt(0);

                if (isNaN(montant)) {
                    montant = parseInt(0);
                }

                let taxe = {
                    id: taxe_id,
                    montant: montant,
                }

                appendToStorage('taxes_modification', taxe);

            });

            let taxes_result = localStorage.getItem('taxes_modification');

            console.log(taxes_result);

            //mettre dans un champ du formulaire de modification; vu que les cookies ne marchent pas, surement à cause du popup load dynamiquement
            $('#modal-modification_police #liste_autres_taxes_modification').val(taxes_result);

        } else {
            notifyWarning('No web storage Support.');
        }


    });

    //FIN GESTION MODIFICATION AUTRES TAXES

    //************* FIN AJOUT ET MODIFICATION DE POLICE ***************//

    //************* AJOUT DE QUITTANCES ***************//
    $("#btnOpenDialogAddQuittance").on('click', function () {

        let model_name = $(this).data('model_name');
        let modal_title = $(this).data('modal_title');
        let href = $(this).data('href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-quittance').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-quittance').find('.modal-title').text(modal_title);
            $('#modal-quittance').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-quittance').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-quittance').modal();

            //Bouton d'enregistrement de la quittance
            $("#btn_save_quittance").on('click', function () {

                let btn_save_quittance = $(this);


                let formulaire = $('#form_add_quittance');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                if (formulaire.valid()) {

                    //désactiver le bouton Valider, pour empecher une double soumission du formulaire
                    btn_save_quittance.attr('disabled', true);

                    //enregistrer les taxes dans le storage
                    $('#modal-autres_taxes_quittance #btn_save_taxe').click();
                    //alert($('#modal-autres_taxes_quittance #btn_save_taxe').text());

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment créer cette quittance ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu
                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formulaire.serialize(),
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });


                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-quittance .alert .message').html(errors_list_to_display);

                                                $('#modal-quittance .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");

                                            btn_save_quittance.removeAttr('disabled');

                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                    btn_save_quittance.removeAttr('disabled');

                                }
                            }
                        ]
                    });
                    //fin demande confirmation


                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');

                    btn_save_quittance.removeAttr('disabled');

                }

            });


            //gestion de la fenetre interne des taxes
            $("#form_add_autres_taxes_quittance .montant_taxe").on('keyup', function (event) {

                if (event.which == 13) {
                    event.preventDefault();
                }

                let montant_total_autres_taxes_quittance = parseInt(0);

                $("#modal-autres_taxes_quittance .montant_taxe").each(function (index, element) {

                    //element = this
                    let montant = parseInt($(element).val().replaceAll(' ', ''));
                    montant = (montant != '') ? montant : parseInt(0);

                    if (isNaN(montant)) {
                        montant = parseInt(0);
                    }

                    montant_total_autres_taxes_quittance += montant;

                });

                $('#modal-quittance #autres_taxes').val(montant_total_autres_taxes_quittance);
                $('#modal-autres_taxes_quittance .total_autres_taxes').text(montant_total_autres_taxes_quittance);

                calculer_montant_divers_quittance();

            });


            //A la fermeture de la fenetre des autres taxes, sauvegarder les données dans les cookies pour pouvoir les récupérer coté serveur
            $('#modal-autres_taxes_quittance').on('hidden.bs.modal', function () {
                $('body').addClass('modal-open');

                //Enregistrer les autres taxes saisies
                if (typeof (Storage) !== "undefined") {

                    localStorage.setItem('taxes_quittance', "");

                    // Code for localStorage
                    $("#modal-autres_taxes_quittance .montant_taxe").each(function (index, element) {

                        //element = this
                        let taxe_id = $(element).attr('data-taxe_id');
                        let montant = parseInt($(element).val().replaceAll(' ', ''));
                        montant = (montant != '') ? montant : parseInt(0);

                        if (isNaN(montant)) {
                            montant = parseInt(0);
                        }

                        let taxe = {
                            id: taxe_id,
                            montant: montant,
                        }

                        appendToStorage('taxes_quittance', taxe);

                    });

                    let taxes_result = localStorage.getItem('taxes_quittance');

                    console.log(taxes_result);

                    //enregistrer dans le cookies pour l'utiliser coté serveur avec python
                    document.cookie = "taxes_quittance=" + taxes_result;


                } else {
                    notifyWarning('No web storage Support.');
                }


            });



        });


    });

    $(document).on("keyup change", "#modal-quittance .calculs_handler_police", function (event) {

        if (event.which == 13) {
            event.preventDefault();
        }

        calculer_montant_divers_quittance();

    });

    function calculer_montant_divers_quittance() {

        let nature_quittance_id = $('#modal-quittance #nature_quittance').val();
        let type_quittance_id = $('#modal-quittance #type_quittance').val();
        let prime_ht = parseInt($('#modal-quittance #prime_ht').val().replaceAll(' ', ''));
        let cout_police_compagnie = parseInt($('#modal-quittance #cout_police_compagnie').val().replaceAll(' ', ''));
        let cout_police_courtier = parseInt($('#modal-quittance #cout_police_courtier').val().replaceAll(' ', ''));
        let taxe = parseInt($('#modal-quittance #taxe').val().replaceAll(' ', ''));
        let autres_taxes = parseInt($('#modal-quittance #autres_taxes').val().replaceAll(' ', ''));

        let taux_com_courtage = $('#modal-quittance #taux_com_courtage').val();
        //let taux_com_courtage_terme = $('#modal-quittance #taux_com_courtage_terme').val();

        console.log('Valeur taux_com_courtage en chaîne:', taux_com_courtage);
        //console.log('Valeur taux_com_courtage_terme en chaîne:', taux_com_courtage_terme);

        // Remplacer la virgule par un point pour garantir une bonne conversion en nombre
        taux_com_courtage = parseFloat(taux_com_courtage.replace(',', '.'));
        //taux_com_courtage_terme = parseFloat(taux_com_courtage_terme.replace(',', '.'));

        // Vérification des valeurs après conversion
        console.log('taux_com_courtage', taux_com_courtage);
        //console.log('taux_com_courtage_terme', taux_com_courtage_terme);

        //Added on 10022024:0302: si terme, prendre le taux_com_courtage_terme comme taux_com_courtage
        if (nature_quittance_id == 2) {
            taux_com_courtage =0 //taux_com_courtage_terme;
        }

        if (isNaN(prime_ht)) { prime_ht = 0; }
        if (isNaN(cout_police_compagnie)) { cout_police_compagnie = 0; }
        if (isNaN(cout_police_courtier)) { cout_police_courtier = 0; }
        if (isNaN(taxe)) { taxe = 0; }
        if (isNaN(autres_taxes)) { autres_taxes = 0; }
        if (isNaN(taux_com_courtage)) { taux_com_courtage = 0; }
        //if (isNaN(taux_com_courtage_terme)) { taux_com_courtage_terme = 0; }

        /* accorder les montant selon la nature de la quittance */
        if ((prime_ht > 0 && nature_quittance_id == 3) || (prime_ht < 0 && nature_quittance_id != 3)) {
            prime_ht = prime_ht * (-1);
        }
        $('#modal-quittance #prime_ht').val(prime_ht);

        let prime_ttc = prime_ht + cout_police_compagnie + cout_police_courtier + taxe + autres_taxes;

        let montant_commission_courtage = (taux_com_courtage / 100) * prime_ht;
        //let montant_commission_courtage_terme = (taux_com_courtage_terme / 100) * prime_ht;

        //selon type de quittance : honnoraire pas de com
        if (type_quittance_id == 2) {
            montant_commission_courtage = 0;
            //montant_commission_courtage_terme = 0;
        }

        console.log('nature_quittance_id', nature_quittance_id);
        console.log('type_quittance_id', type_quittance_id);
        console.log('prime_ht', prime_ht);
        console.log('cout_police_compagnie', cout_police_compagnie);
        console.log('cout_police_courtier', cout_police_courtier);
        console.log('taxe', taxe);
        console.log('autres_taxes', autres_taxes);
        console.log('taux_com_courtage', taux_com_courtage);
        //console.log('taux_com_courtage_terme', taux_com_courtage_terme);
        console.log('montant_commission_courtage', montant_commission_courtage);
        //console.log('montant_commission_courtage_terme', montant_commission_courtage_terme);
        console.log('prime_ttc', prime_ttc);

        let total_taux_com_affaire_nouvelle = 0;
        let total_taux_com_renouvelement = 0;
        let montant_commission_intermediaire = 0;
        let total_montant_commission_intermediaire = 0;

        $('.taux_com_affaire_nouvelle').each(function () {

            let taux_com_affaire_nouvelle = parseFloat($(this).val());
            let taux_com_renouvelement = parseFloat($(this).closest('tr').find('.taux_com_renouvelement').val());
            let base_calcul_taux_retrocession = $(this).closest('tr').find('.base_calcul_taux_retrocession').val();
            let intermediaire = $(this).closest('tr').find('.intermediaire').val();

            if (intermediaire != "" && base_calcul_taux_retrocession != "" && taux_com_affaire_nouvelle > 0) {

                if (nature_quittance_id == 1) {//quittance comptant: on prend les taux de com affaire nouvelle

                    if (base_calcul_taux_retrocession == 1) {//sur prime ht

                        montant_commission_intermediaire = (taux_com_affaire_nouvelle / 100) * prime_ht;

                    } else if (base_calcul_taux_retrocession == 2) {//sur com courtage

                        montant_commission_intermediaire = (taux_com_affaire_nouvelle / 100) * montant_commission_courtage;

                    } else if (base_calcul_taux_retrocession == 4) {//sur com total (courtage + gestion)

                        montant_commission_intermediaire = (taux_com_affaire_nouvelle / 100) * (montant_commission_courtage);

                    }

                } else if (nature_quittance_id == 2) {//quittance Terme: on prend les taux de com renouvellement

                    if (base_calcul_taux_retrocession == 1) {//sur prime ht

                        montant_commission_intermediaire = (taux_com_renouvelement / 100) * prime_ht;

                    } else if (base_calcul_taux_retrocession == 2) {//sur com courtage

                        montant_commission_intermediaire = (taux_com_renouvelement / 100) * montant_commission_courtage;

                    } else if (base_calcul_taux_retrocession == 4) {//sur com total (courtage + gestion)

                        montant_commission_intermediaire = (taux_com_renouvelement / 100) * (montant_commission_courtage);

                    }

                }

                console.log('montant_commission_intermediaire', montant_commission_intermediaire);

                total_montant_commission_intermediaire = montant_commission_intermediaire; // a la place de celui es ten bas
                // total_montant_commission_intermediaire = total_montant_commission_intermediaire + montant_commission_intermediaire;

                console.log('total_montant_commission_intermediaire', total_montant_commission_intermediaire);

            }

        });

        $('#modal-quittance #prime_ttc').val(prime_ttc);

        $('#modal-quittance #commission_courtage').val(montant_commission_courtage);

        //$('#modal-quittance #commission_courtage_terme').val(montant_commission_courtage_terme);

        $('#modal-quittance #total_commission_intermediaire').val(total_montant_commission_intermediaire);
    }

    $(document).on("change", "#modal-quittance #nature_quittance", function (event) {
        let nature_quittance_id = $(this).val();

        if (nature_quittance_id == 1) {
            $('.show_if_nature_quittance_terme').hide();
            $('.show_if_nature_quittance_comptant').show();
        } else {
            $('.show_if_nature_quittance_comptant').hide();
            $('.show_if_nature_quittance_terme').show();
        }

    });
    //************* FIN AJOUT DE QUITTANCES ***************//

    let documentsDataTable;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    //********* DETAILS QUITTANCE ***********//
    function initializeDataTable(tableId){

        if (!$(tableId).length) {
            console.warn(`Table non trouvée pour l'ID : ${tableId}`);
            return;
        }

        if (!$.fn.DataTable.isDataTable(tableId)) {
            const dtConfig = {
                "language": { "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json" },
                order: [[0, 'desc']],
                lengthMenu: [[5, 10, 25, 50, 100], [5, 10, 25, 50, 100]],
                responsive: true
            };

            if (tableId === '#table_document_quittance') {
                Object.assign(dtConfig, {
                    paging: false,
                    ordering: false,
                    info: false,
                    searching: false
                });
                window.documentsDataTable = $(tableId).DataTable(dtConfig);
            } else {
                $(tableId).DataTable(dtConfig);
            }
        } else if (tableId === '#table_document_quittance') {
            window.documentsDataTable = $(tableId).DataTable();
        }
    }

    $(".btnOpenDialogDetailQuittance").on('dblclick', function () {
        $(".btnOpenDialogDetailQuittance").removeClass('tr_selected');
        $(this).addClass('tr_selected');

        let model_name = $(this).data('model_name');
        let modal_title = $(this).data('modal_title');
        let href = $(this).data('href');
        let quittance_id = $(this).data('quittance_id');

        console.log(href);
        console.log(quittance_id);

        $('#olea_std_dialog_box').load(href, function () {
            AppliquerMaskSaisie();

            const $modal = $('#modal-details_quittance');
            $modal.attr('data-backdrop', 'static').attr('data-keyboard', false);
            $modal.find('.modal-title').text(modal_title);
            $modal.find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $modal.find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            setTimeout(() => {
                initializeDataTable('#table_reglements');
                initializeDataTable('#table_bordereau_encaissement_compagnie');
                initializeDataTable('#table_bordereau_reversement_compagnie');
                initializeDataTable('#table_document_quittance');
            }, 50); // délai court pour laisser le DOM se mettre à jour

            if (quittance_id) {
                const documentsApiUrl = `/production/get_documents_quittance_session/?quittance_id=${quittance_id}`;
                fetchAndDisplayDocuments(documentsApiUrl);
            }

            $modal.modal();

            $('#btn_save_document').off('click').on('click', function (e) {
                handleAddDocument(e);
            });

            $('#chargementDocumentQuittance').off('change').on('change', function () {
                const currentQuittanceId = $(this).val();
                if (currentQuittanceId) {
                    const documentsApiUrl = `/production/get_documents_quittance_session/?quittance_id=${currentQuittanceId}`;
                    fetchAndDisplayDocuments(documentsApiUrl);
                } else {
                    documentsDataTable.clear().draw();
                }
            });
        });
    });

    function fetchAndDisplayDocuments(url) {
        $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json',
            success: function (response) {
                if (response && response.success && response.data) {
                    documentsDataTable.clear();
                    response.data.forEach(function (document) {
                        let fileLink = `<a target="_blank" href="${document.fichier_url}"><i class="fa fa-file" title="Aperçu"></i> Afficher</a>`;
                        let actionsHtml = `
                            <span class="btn_supprimer_document" data-document_id="${document.id}" onclick="supprimer_document(${document.id})" style="cursor:pointer;"><i class="fa fa-times text-danger"></i> </span>&nbsp;&nbsp;&nbsp;
                            <span class="btn_modifier_on_modal" data-model_name="document" data-href="${document.modifier_url || '#'}" data-modal_title="Modification d'un document" title="Modifier" style="cursor:pointer;"><i class="fas fa-edit text-warning"></i></span>
                        `;
                        documentsDataTable.row.add([
                            document.nom || '',
                            document.type_libelle || '',
                            fileLink,
                            document.date_creation || '',
                            actionsHtml
                        ]);
                    });
                    documentsDataTable.draw();
                } else {
                    documentsDataTable.clear().draw();
                }
            },
            error: function (xhr, status, error) {
                console.error("Erreur chargement documents :", status, error, xhr.responseText);
            }
        });
    }

    function handleAddDocument(e) {
        if (e && e.preventDefault) e.preventDefault();

        const form = $('#modal_form_document')[0];
        const formData = new FormData(form);
        const actionUrl = form.action;
        const alertBox = $('#modal-document_quittance .alert');

        alertBox.removeClass('hidden').addClass('alert-info').find('.message').text('TRAITEMENT EN COURS...');
        $('.champ_obligatoire').removeClass('is-invalid is-valid');

        let valide = true;
        $('.champ_obligatoire').each(function () {
            const value = $(this).val();
            if ($(this).attr('type') === 'file') {
                if (this.files.length === 0) {
                    $(this).addClass('is-invalid');
                    valide = false;
                } else {
                    $(this).addClass('is-valid');
                }
            } else if (!value || value.trim() === '') {
                $(this).addClass('is-invalid');
                valide = false;
            } else {
                $(this).addClass('is-valid');
            }
        });

        if (!valide) {
            alertBox.removeClass('alert-info').addClass('alert-danger').find('.message').text('Veuillez remplir tous les champs obligatoires.');
            setTimeout(() => { alertBox.addClass('hidden').removeClass('alert-danger'); }, 3000);
            return;
        }

        $.ajax({
            url: actionUrl,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            success: function (response) {
                if (response.statut === 1) {
                    alertBox.removeClass('alert-info').addClass('alert-success').find('.message').text(response.message || 'Document ajouté avec succès !');

                    const newDocument = response.data;
                    const fileHtml = newDocument.fichier;
                    const actionsHtml = `
                        <span class="btn_supprimer_document" data-document_id="${newDocument.id}" onclick="supprimer_document(${newDocument.id})" style="cursor:pointer;"><i class="fa fa-times text-danger"></i> </span>&nbsp;&nbsp;&nbsp;
                        <span class="btn_modifier_on_modal" data-model_name="document" data-href="${newDocument.modifier_url || '#'}" data-modal_title="Modification d'un document" title="Modifier" style="cursor:pointer;"><i class="fas fa-edit text-warning"></i></span>
                    `;

                    documentsDataTable.row.add([
                        newDocument.nom || '',
                        newDocument.type_document || '',
                        fileHtml,
                        new Date().toLocaleDateString('fr-FR') || '',
                        actionsHtml
                    ]).draw(false);

                    form.reset();
                    $('.champ_obligatoire').removeClass('is-valid is-invalid');
                    $("#modal_form_document select").prop('selectedIndex', 0).trigger('change');

                    setTimeout(() => { alertBox.addClass('hidden').removeClass('alert-success'); }, 3000);
                } else {
                    alertBox.removeClass('alert-info').addClass('alert-danger').find('.message').text(response.message || 'Erreur lors de l\'ajout du document.');
                    console.error("Erreur côté serveur :", response.message, response.errors);
                }
            },
            error: function (xhr, status, error) {
                alertBox.removeClass('alert-info').addClass('alert-danger').find('.message').text('Une erreur est survenue.');
                console.error("Erreur Ajax ajout document :", status, error, xhr.responseText);
            }
        });
    }


    //********* FIN DETAILS QUITTANCE ***********//


    //********* FAIRE UN REGLEMENT ***********//

    $("#btnOpenDialogAddReglement").on('click', function () {

        let model_name = $(this).data('model_name');
        let modal_title = $(this).data('modal_title');
        let href = $(this).data('href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-reglement').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-reglement').find('.modal-title').text(modal_title);
            $('#modal-reglement').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-reglement').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-reglement').modal();

            //gestion des saisies des montants à regler
            $(document).on('change', '.checkbox_quittance_a_regler', function () {
                let input_montant_a_regler = $(this).closest('tr').find('.montant_a_regler');
                let solde_quittance = $(this).closest('tr').find('.solde_quittance').val();
                let input_solde_apres = $(this).closest('tr').find('.solde_apres');

                calculer_montant_total_a_regler();

                if (this.checked) {
                    input_montant_a_regler.val(solde_quittance);
                    input_solde_apres.val(0);
                    input_montant_a_regler.removeAttr('readonly');
                    input_montant_a_regler.attr('required', true);

                    // Déclencher l'événement 'change' manuellement
                    input_montant_a_regler.trigger('change');
                } else {
                    input_montant_a_regler.val(0);
                    input_solde_apres.val(solde_quittance);
                    input_montant_a_regler.attr('readonly', true);
                    input_montant_a_regler.removeAttr('required');

                    // Déclencher l'événement 'change' manuellement
                    input_montant_a_regler.trigger('change');
                }

            });

            //montant_a_regler
            $(document).on('change keyup', '.handle_calculer_montant_total_a_regler', function () {
                console.log('handle_calculer_montant_total_a_regler');
                calculer_montant_total_a_regler();

            });

            //champs obligatoires variables selon le mode de règlement
            $(document).on('change', '#mode_reglement', function () {
                //si espèce
                if ($(this).val() == 1) {
                    $('#numero_piece').removeAttr('required');
                    $('#banque').removeAttr('required');
                    $('#libelle_numero_piece_required').html('');
                    $('#libelle_banque_required').html('');
                } else {
                    $('#numero_piece').attr('required', true);
                    // $('#banque').attr('required', true);
                    $('#libelle_numero_piece_required').html('*');
                    // $('#libelle_banque_required').html('*');
                }

            });

            //enregistrement
            $('#btn_save_reglement').on('click', function () {

                let btn_save_reglement = $(this);

                let formulaire = $('#form_add_reglement');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                if (formulaire.valid()) {

                    //désactiver le bouton Valider, pour empecher une double soumission du formulaire
                    btn_save_reglement.attr('disabled', true);

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment effectuer ce règlement ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu
                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formulaire.serialize(),
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                location.reload();

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-reglement .alert .message').html(errors_list_to_display);

                                                $('#modal-reglement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");

                                            btn_save_reglement.removeAttr('disabled');

                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                    btn_save_reglement.removeAttr('disabled');

                                }
                            }
                        ]
                    });
                    //fin demande confirmation


                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');

                    btn_save_reglement.removeAttr('disabled');

                }


            });

        });

    });

    function calculer_montant_total_a_regler() {

        let montant_total_a_regler = 0;

        $('.montant_a_regler').each(function (element) {

            let montant_a_regler = parseFloat($(this).val().replaceAll(' ', ''));
            let solde_quittance = $(this).closest('tr').find('.solde_quittance').val();
            let solde_apres = solde_quittance;//init

            if (montant_a_regler > 0 && montant_a_regler <= solde_quittance) {

                console.log(montant_a_regler + ' réglé sur ' + solde_quittance);
                montant_total_a_regler = montant_total_a_regler + montant_a_regler;

                solde_apres = solde_quittance - montant_a_regler;

            } else {
                solde_apres = solde_quittance;
                $(this).val('0');
            }

            $(this).closest('tr').find('.solde_apres').val(solde_apres);

        });

        $('.montant_total_a_regler').val(montant_total_a_regler);

        if (montant_total_a_regler > 0) {
            $('#btn_save_reglement').removeAttr('disabled');
        } else {
            $('#btn_save_reglement').attr('disabled', 'true');
        }

    }

    //********* FIN FAIRE UN REGLEMENT ***********//


    //********* FAIRE UN LETTRAGE ***********//

    $("#btnOpenDialogAddLettrage").on('click', function() {
        let model_name = $(this).data('model_name');
        let modal_title = $(this).data('modal_title');
        let href = $(this).data('href');

        $('#olea_std_dialog_box').load(href, function() {
            AppliquerMaskSaisie();

            $('#modal-lettrage').attr('data-backdrop', 'static').attr('data-keyboard', false);
            $('#modal-lettrage').find('.modal-title').text(modal_title);
            $('#modal-lettrage').find('#btn_valider').attr({'data-model_name': model_name, 'data-href': href});
            $('#modal-lettrage').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');
            $('#modal-lettrage').modal();

            function updateTotalARegler() {
                let total = 0;
                $('.montant_a_regler').each(function() {
                    total += parseFloat($(this).val().replace(/\s/g, '').replace(',', '.')) || 0;
                });
                $('.montant_total_a_regler').val(total.toFixed(2));
                console.log('Montant total à régler :', total.toFixed(2));
            }

            function calculerMontantTotalAcomptes() {
                // Cette fonction calcule seulement le total des acomptes cochés
                let total_acomptes = 0;
                $('.checkbox_acompte_a_utiliser:checked').each(function() {
                    const row = $(this).closest('tr');
                    const solde = parseFloat(row.find('.solde_acompte').val().replace(/\s/g, '').replace(',', '.')) || 0;
                    total_acomptes += solde;
                });
                return total_acomptes;
            }

            function updateAcompteCumulEtRestant() {
                // On calcule d'abord le total des acomptes cochés
                let montant_total_acomptes = calculerMontantTotalAcomptes();
                console.log('Total des acomptes cochés:', montant_total_acomptes.toFixed(2));

                // Réinitialiser tous les soldes restants d'acompte
                $('.checkbox_acompte_a_utiliser').each(function() {
                    const row = $(this).closest('tr');
                    const solde = parseFloat(row.find('.solde_acompte').val().replace(/\s/g, '').replace(',', '.')) || 0;

                    if ($(this).is(':checked')) {
                        // Par défaut, on considère que tout l'acompte sera utilisé
                        row.find('.solde_restant_acompte').val('0.00');
                    } else {
                        // Si l'acompte n'est pas coché, le solde restant est égal au solde initial
                        row.find('.solde_restant_acompte').val(solde.toFixed(2));
                    }
                });

                // Maintenant calculons le total des quittances cochées pour savoir combien d'acomptes seront utilisés
                let montant_total_quittances = 0;
                $('.checkbox_quittance_a_regler:checked').each(function() {
                    const row = $(this).closest('tr');
                    const solde = parseFloat(row.find('.solde_quittance').val().replace(/\s/g, '').replace(',', '.')) || 0;
                    montant_total_quittances += solde;
                });
                console.log('Total des quittances cochées:', montant_total_quittances.toFixed(2));

                // Calculer le montant restant après affectation aux quittances
                let montant_restant = montant_total_acomptes;

                // Si le total des quittances est inférieur au total des acomptes,
                if (montant_total_quittances < montant_total_acomptes) {
                    const montant_a_utiliser = montant_total_quittances;
                    let montant_deja_utilise = 0;

                    // On parcourt les acomptes cochés sauf le dernier
                    const acomptes_coches = $('.checkbox_acompte_a_utiliser:checked');
                    const nb_acomptes = acomptes_coches.length;

                    if (nb_acomptes > 0) {
                        acomptes_coches.each(function(index) {
                            const row = $(this).closest('tr');
                            const solde = parseFloat(row.find('.solde_acompte').val().replace(/\s/g, '').replace(',', '.')) || 0;

                            // Pour tous les acomptes sauf le dernier
                            if (index < nb_acomptes - 1) {
                                if (montant_deja_utilise + solde <= montant_a_utiliser) {
                                    // Cet acompte est entièrement utilisé
                                    row.find('.solde_restant_acompte').val('0.00');
                                    montant_deja_utilise += solde;
                                } else {
                                    // Cet acompte n'est que partiellement utilisé
                                    const montant_utilise = montant_a_utiliser - montant_deja_utilise;
                                    const solde_restant = solde - montant_utilise;
                                    row.find('.solde_restant_acompte').val(solde_restant.toFixed(2));
                                    montant_deja_utilise = montant_a_utiliser; // On a tout utilisé
                                }
                            } else {
                                // Pour le dernier acompte coché
                                const montant_restant_a_utiliser = montant_a_utiliser - montant_deja_utilise;
                                if (montant_restant_a_utiliser < solde) {
                                    // Le dernier acompte n'est que partiellement utilisé
                                    const solde_restant = solde - montant_restant_a_utiliser;
                                    row.find('.solde_restant_acompte').val(solde_restant.toFixed(2));
                                } else {
                                    // Le dernier acompte est entièrement utilisé
                                    row.find('.solde_restant_acompte').val('0.00');
                                }
                            }
                        });
                    }

                    // Le montant disponible est le total des acomptes moins ce qui est utilisé pour les quittances
                    montant_restant = montant_total_acomptes - montant_total_quittances;
                } else {
                    // Si le total des quittances est supérieur ou égal au total des acomptes,
                    montant_restant = 0;
                }

                // Maintenant mettons à jour le montant cumulé des acomptes disponibles
                let montant_disponible = montant_total_acomptes

                // Mise à jour des champs de cumul d'acomptes
                const montant_format = montant_disponible.toFixed(2);
                $('#hidden_select_montant_acompte_cumul').val(montant_format);
                $('#montant_acompte_cumul').val(montant_format);

                // Mise à jour de la couleur de fond en fonction du montant disponible
                if (montant_disponible > 0) {
                    $('#montant_acompte_cumul').css('background', 'green');
                } else {
                    $('#montant_acompte_cumul').css('background', '#dc3545'); // Rouge pour 0 ou négatif
                }

                console.log('Montant acompte cumulé disponible:', montant_format);
                return montant_disponible; // Retourne le montant disponible pour être utilisé par d'autres fonctions
            }

            function updateMontantsQuittances() {
                // Obtenir le montant disponible des acomptes
                let montant_disponible = parseFloat($('#hidden_select_montant_acompte_cumul').val().replace(/\s/g, '').replace(',', '.')) || 0;
                console.log('Début traitement quittances. Montant disponible initial :', montant_disponible.toFixed(2));

                // On recalcule ce montant disponible car il pourrait avoir changé si de nouveaux acomptes ont été cochés
                if (montant_disponible === 0) {
                    montant_disponible = calculerMontantTotalAcomptes();
                }

                // Traiter chaque ligne de quittance
                $('.checkbox_quittance_a_regler').each(function() {
                    const row = $(this).closest('tr');
                    const solde = parseFloat(row.find('.solde_quittance').val().replace(/\s/g, '').replace(',', '.')) || 0;
                    const montant_field = row.find('.montant_a_regler');
                    const montant_transmit_field = row.find('.montant_a_regler_transmit');
                    const solde_apres_field = row.find('.solde_apres');
                    const solde_apres_transmit = row.find('.solde_apres_transmit');

                    if ($(this).is(':checked')) {
                        if (montant_disponible >= solde) {
                            // On peut régler toute la quittance
                            montant_field.val(solde.toFixed(2)).attr('readonly', true);
                            solde_apres_field.val('0.00');
                            montant_disponible -= solde;
                        } else {
                            // On ne peut régler que partiellement la quittance
                            montant_field.val(montant_disponible.toFixed(2)).attr('readonly', true);
                            solde_apres_field.val((solde - montant_disponible).toFixed(2));
                            montant_disponible = 0;
                        }
                    } else {
                        // Quittance non cochée, donc pas de montant à régler
                        montant_field.val('0.00').attr('readonly', true);
                        solde_apres_field.val(solde.toFixed(2));
                    }

                    // Mettre à jour les champs cachés pour la transmission
                    montant_transmit_field.val(montant_field.val());
                    solde_apres_transmit.val(solde_apres_field.val());

                    console.log('Quittance - Solde: ' + solde +
                        ', Montant à régler: ' + montant_field.val() +
                        ', Solde après: ' + solde_apres_field.val());
                });

                // Le montant disponible d'acomptes est maintenant mis à jour
                const montant_format = montant_disponible.toFixed(2);
                $('#hidden_select_montant_acompte_cumul').val(montant_format);
                $('#montant_acompte_cumul').val(montant_format);

                // Mettre à jour la couleur du fond en fonction du montant
                if (montant_disponible > 0) {
                    $('#montant_acompte_cumul').css('background', 'green');
                } else {
                    $('#montant_acompte_cumul').css('background', '#dc3545'); // Rouge pour 0 ou négatif
                }

                console.log('Montant restant disponible après affectation quittances :', montant_format);
            }

            function verifier_activation_bouton_lettrage() {
                const acompte_cumul = parseFloat($('#hidden_select_montant_acompte_cumul').val()) || 0;
                const montant_total = parseFloat($('.montant_total_a_regler').val().replace(',', '.')) || 0;
                const has_quittance = $('.checkbox_quittance_a_regler:checked').length > 0;
                const has_acompte = $('.checkbox_acompte_a_utiliser:checked').length > 0;

                const is_enabled = has_acompte && has_quittance && montant_total > 0;
                $('#btn_save_lettrage').prop('disabled', !is_enabled);
            }

            function refreshAll() {
                // On recalcule d'abord le montant total des acomptes disponibles
                updateAcompteCumulEtRestant();
                updateMontantsQuittances();
                updateTotalARegler();
                verifier_activation_bouton_lettrage();
            }

            $(document).on('change', '.checkbox_acompte_a_utiliser, .checkbox_quittance_a_regler', refreshAll);

            $('#btn_save_lettrage').on('click', function() {
                const btn = $(this);
                const form = $('#form_add_lettrage');
                const href = form.attr('action');

                $.validator.setDefaults({
                    ignore: []
                });

                if (form.valid()) {
                    btn.attr('disabled', true);
                    const n = noty({
                        text: 'Voulez-vous effectuer ce lettrage de compte ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [{
                                addClass: 'btn btn-primary',
                                text: 'OUI',
                                onClick: function($noty) {
                                    $noty.close();
                                    // 🔍 Log des données envoyées
                                    console.log('Données envoyées :', form.serialize());
                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: form.serialize(),
                                        success: function(response) {
                                            if (response.statut == 1) {
                                                notifySuccess(response.message, function() {
                                                    location.reload();
                                                });
                                            } else {
                                                let errors = '';
                                                $.each(response.errors, function(field, message) {
                                                    errors += '- ' + ucfirst(field) + ': ' + message + '<br/>';
                                                });
                                                $('#modal-lettrage .alert .message').html(errors);
                                                $('#modal-lettrage .alert')
                                                    .fadeTo(2000, 500)
                                                    .slideUp(500)
                                                    .removeClass('alert-success')
                                                    .addClass('alert-warning');
                                            }
                                        },
                                        error: function() {
                                            notifyWarning("Erreur lors de l'enregistrement");
                                            btn.removeAttr('disabled');
                                        }
                                    });
                                }
                            },
                            {
                                addClass: 'btn btn-danger',
                                text: 'Annuler',
                                onClick: function($noty) {
                                    $noty.close();
                                    btn.removeAttr('disabled');
                                }
                            }
                        ]
                    });
                } else {
                    $('label.error').hide().removeClass('error').text('');
                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                    btn.removeAttr('disabled');
                }
            });

            // Initialisation
            refreshAll();
        });
    });

    //********* FIN FAIRE UN LETTRAGE ***********//



    //********* FAIRE UN ENCAISSEMENT DE COMMISSION ***********//

    $(".btnOpenDialogDetailCompagnieEncaissement").on('dblclick', function () {

        $(".btnOpenDialogDetailCompagnieEncaissement").removeClass('tr_selected');
        $(this).addClass('tr_selected');
        let compagnie = $(this).data('compagnie');
        $("#btnOpenDialogAddEncaissementCommision").trigger("click");

    });


    $("#btnOpenDialogAddEncaissementCommision").on('click', function () {

        let model_name = $(this).data('model_name');
        let modal_title = $(this).data('modal_title');
        let href = $(this).data('href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-encaissement').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-encaissement').find('.modal-title').text(modal_title);
            $('#modal-encaissement').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-encaissement').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-encaissement').modal();

            $('#modal-encaissement').on('shown.bs.modal', function () {
                compagnie = $('.tr_selected').data('compagnie');
                if (compagnie && compagnie != "") {
                    $('#modal-encaissement #compagnie option[value=' + compagnie + ']').attr('selected', 'selected');
                    $("#modal-encaissement #compagnie").trigger('change');
                }
            })

            //gestion des saisies des montants à regler
            $(document).on('change', '.checkbox_quittance_a_encaisser', function () {
                let input_montant_encaisse_court = $(this).closest('tr').find('.montant_encaisse_court');
                let input_montant_encaisse_gest = $(this).closest('tr').find('.montant_encaisse_gest');
                let solde_quittance = $(this).closest('tr').find('.solde_quittance').val();
                let input_solde_apres = $(this).closest('tr').find('.solde_apres');
                let montant_com_solde = parseFloat($(this).data('montant_com_solde'));
                let montant_com_courtage = 0; //parseFloat($(this).data('reglement_montant_com_courtage'));
                let montant_com_gestion = 0; //parseFloat($(this).data('reglement_montant_com_gestion'));


                //input_montant_a_encaisser.val(0);
                input_solde_apres.val(solde_quittance);
                //$('#restant_total').val(montant_com_solde);
                $(this).closest('tr').find('.restant_total').val(montant_com_solde);

                if (this.checked) {
                    input_montant_encaisse_court.removeAttr('readonly');
                    input_montant_encaisse_court.attr('required', true);
                    input_montant_encaisse_court.val(0);//montant_com_courtage;
                    input_montant_encaisse_gest.removeAttr('readonly');
                    input_montant_encaisse_gest.attr('required', true);
                    input_montant_encaisse_gest.val(0);//montant_com_gestion);
                } else {
                    input_montant_encaisse_court.attr('readonly', true);
                    input_montant_encaisse_court.removeAttr('required');
                    input_montant_encaisse_court.val(0);
                    input_montant_encaisse_gest.attr('readonly', true);
                    input_montant_encaisse_gest.removeAttr('required');
                    input_montant_encaisse_gest.val(0);
                }

                calculer_montant_total_a_encaisser();


            });

            //montant_a_regler
            $(document).on('change keyup', '.handle_calculer_montant_total_a_encaisser', function () {
                //console.log('handle_calculer_montant_total_a_encaisser');
                calculer_montant_total_a_encaisser();

            });

            $(document).on('change keyup', '#debit_difference', function () {
                $('#credit_difference').val("");
                //calculer_montant_total_a_encaisser();
            });
            $(document).on('change keyup', '#credit_difference', function () {
                $('#debit_difference').val("");
                //calculer_montant_total_a_encaisser();
            });

            $(document).on('change', '#modal-encaissement #compagnie', function () {
                let href_reglements_reverses = $(this).children('option:selected').data('href_reglements_reverses');

                calculer_montant_total_a_encaisser();//vider les champs d'aperçu

                $('.montant_total_com').val(0);

                $('#btn_save_encaissement').attr('disabled', 'true');

                $('#box_reglements_reverses').load(href_reglements_reverses, function () {
                    $('#table_reglements_reverses').DataTable({
                        "language": {
                            "url": "../../static/admin_custom/js/French.json"
                        },
                        //order: [[0, 'desc']],
                        lengthMenu: [
                            [10, 25, 50, 100, -1], [10, 25, 50, 100, "Tout"]
                        ],
                        //sDom: "<'row'<'col-sm-6'>>t<'row'<'col-sm-6'><'col-sm-6'>>",
                        paging: false,
                        searching: true,
                        lengthChange: true,
                        bSort: false,
                        scrollX: true,
                    });
                });

            });


            //champs obligatoires variables selon le mode de règlement
            $(document).on('change', '#mode_reglement', function () {
                //si espèce
                if ($(this).val() == 1) {
                    $('#numero_piece').removeAttr('required');
                    $('#banque').removeAttr('required');
                    $('#libelle_numero_piece_required').html('');
                    $('#libelle_banque_required').html('');
                } else {
                    $('#numero_piece').attr('required', true);
                    // $('#banque').attr('required', true);
                    $('#libelle_numero_piece_required').html('*');
                    // $('#libelle_banque_required').html('*');
                }

            });

            //enregistrement
            $('#btn_save_encaissement').on('click', function () {

                let btn_save_encaissement = $(this);

                let formulaire = $('#form_add_encaissement_commission');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                if (formulaire.valid()) {

                    //désactiver le bouton Valider, pour empecher une double soumission du formulaire
                    btn_save_encaissement.attr('disabled', true);

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment effectuer cet encaissement ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu
                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formulaire.serialize(),
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    window.open('../generer_bordereau_encaissement_compagnie_pdf/' + response.data.operation_id, '_blank');
                                                    location.reload();
                                                });


                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-encaissement .alert .message').html(errors_list_to_display);

                                                $('#modal-encaissement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");

                                            btn_save_encaissement.removeAttr('disabled');

                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                    btn_save_encaissement.removeAttr('disabled');

                                }
                            }
                        ]
                    });
                    //fin demande confirmation


                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');

                    btn_save_encaissement.removeAttr('disabled');

                }

            });

        });

    });


    function calculer_montant_total_a_encaisser() {

        let montant_total_reglements_coches = 0;
        let montant_total_a_regler_compagnie = 0;
        let montant_total_com_gestion = 0;
        let montant_total_com_courtage = 0;
        let montant_total_a_encaisser = 0;
        let montant_solde = 0;
        let difference_match = false;
        let erreur_difference = false;


        let credit_difference = $('#credit_difference').val().replaceAll(" ", "");
        credit_difference = credit_difference === "" || isNaN(credit_difference) ? 0 : parseFloat(credit_difference);
        let debit_difference = parseFloat($('#debit_difference').val().replaceAll(" ", ""));
        debit_difference = debit_difference === "" || isNaN(debit_difference) ? 0 : parseFloat(debit_difference);

        $('.checkbox_quittance_a_encaisser:checked').each(function (element) {

            let montant_reglement = parseFloat($(this).data('reglement_montant'));
            let montant_compagnie = parseFloat($(this).data('reglement_montant_compagnie'));
            let montant_com_gestion = parseFloat($(this).data('reglement_montant_com_gestion'));
            let montant_com_courtage = parseFloat($(this).data('reglement_montant_com_courtage'));

            let montant_a_encaisser = parseFloat($(this).closest('tr').find('.montant_a_encaisser').val());
            //montant_a_encaisser = montant_a_encaisser === "" ? 0 : parseFloat(montant_a_encaisser);
            let montant_a_encaisser_court = parseFloat($(this).closest('tr').find('.montant_encaisse_court').val().replaceAll(" ", ""));
            montant_a_encaisser_court = montant_a_encaisser_court === "" || isNaN(montant_a_encaisser_court) ? 0 : parseFloat(montant_a_encaisser_court);
            let montant_a_encaisser_gest = parseFloat($(this).closest('tr').find('.montant_encaisse_gest').val().replaceAll(" ", ""));
            montant_a_encaisser_gest = montant_a_encaisser_gest === "" || isNaN(montant_a_encaisser_gest) ? 0 : parseFloat(montant_a_encaisser_gest);

            montant_total_reglements_coches = montant_total_reglements_coches + montant_reglement;
            montant_total_a_regler_compagnie = montant_total_a_regler_compagnie + montant_compagnie;
            montant_total_com_gestion = montant_total_com_gestion + montant_a_encaisser_gest;
            montant_total_com_courtage = montant_total_com_courtage + montant_a_encaisser_court;
            //montant_total_a_encaisser       = montant_total_a_encaisser + montant_a_encaisser;
            montant_total_a_encaisser = montant_total_com_courtage + montant_total_com_gestion;

            difference = montant_com_courtage - montant_a_encaisser_court + montant_com_gestion - montant_a_encaisser_gest
            $(this).closest('tr').find('.restant_total').val(difference);

            if (debit_difference == difference && difference_match == false && difference > 0 && difference < 3000) {
                difference_match = true;
            }

            if (difference < 0) {
                erreur_difference = true;
            }

            if (montant_com_courtage < montant_a_encaisser_court || montant_com_gestion < montant_a_encaisser_gest) {
                erreur_difference = true;
            }

            montant_solde = montant_solde + difference;

        });

        $('.montant_total_reglements_coches').val(montant_total_reglements_coches);
        $('.montant_total_a_regler_compagnie').val(montant_total_a_regler_compagnie);
        $('.montant_total_com_gestion').val(montant_total_com_gestion);
        $('.montant_total_com_courtage').val(montant_total_com_courtage);
        $('.montant_total_com').val(montant_total_a_encaisser + credit_difference);
        //$('.montant_total_com').val(montant_total_a_encaisser);

        if (montant_total_a_encaisser > 0 || (montant_total_a_encaisser == 0 && debit_difference > 0)) {
            $('#btn_save_encaissement').removeAttr('disabled');
        } else {
            $('#btn_save_encaissement').attr('disabled', 'true');
        }

        if (((credit_difference > 0 || debit_difference > 0) && $('#compte_difference').val() == "") || debit_difference > 3000 || (debit_difference > 0 && difference_match == false) || ($('#compte_difference').val() != "" && debit_difference == 0 && credit_difference == 0) || (montant_solde > 0 && credit_difference > 0) || erreur_difference == true) {
            $('#btn_save_encaissement').attr('disabled', 'true');
        }

    }


    //********* FIN FAIRE UN ENCAISSEMENT ***********//


    //********* FAIRE UN ENCAISSEMENT DE COMMISSION COURTAGE / GESTION ***********//

    $(".btnOpenDialogDetailCompagnieEncaissementCourtGest").on('dblclick', function () {

        $(".btnOpenDialogDetailCompagnieEncaissementCourtGest").removeClass('tr_selected');
        $(this).addClass('tr_selected');
        let compagnie = $(this).data('compagnie');
        $("#datatable_stock_input_com").html("");
        $("#btnOpenDialogAddEncaissementCommisionCourtGest").trigger("click");

    });

    $("#btnOpenDialogAddEncaissementCommisionCourtGest").on('click', function () {

        let model_name = $(this).data('model_name');
        let modal_title = $(this).data('modal_title');
        let href = $(this).data('href');
        $("#datatable_stock_input_com").html("");

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-encaissement-court-gest').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-encaissement-court-gest').find('.modal-title').text(modal_title);
            $('#modal-encaissement-court-gest').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-encaissement-court-gest').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-encaissement-court-gest').modal();

            $('#modal-encaissement-court-gest').on('shown.bs.modal', function () {
                compagnie = typeof $('.tr_selected') !== 'undefined' ? $('.tr_selected').data('compagnie') : "";
                if (compagnie && compagnie != "") {
                    $('#modal-encaissement-court-gest #compagnie option[value=' + compagnie + ']').attr('selected', 'selected');
                    $("#modal-encaissement-court-gest #compagnie").trigger('change');
                }
            })

            //gestion des saisies des montants à regler
            $(document).on('click', '.checkbox_quittance_a_encaisser_com_gest', function () {
                let input_montant_encaisse_court = $(this).closest('tr').find('.montant_encaisse_court');
                let input_montant_encaisse_gest = $(this).closest('tr').find('.montant_encaisse_gest');
                let solde_quittance = $(this).closest('tr').find('.solde_quittance').val();
                let input_solde_apres = $(this).closest('tr').find('.solde_apres');
                let montant_com_solde = parseFloat($(this).data('montant_com_solde'));
                let montant_com_courtage = 0; //parseFloat($(this).data('reglement_montant_com_courtage'));
                let montant_com_gestion = 0; //parseFloat($(this).data('reglement_montant_com_gestion'));
                let com_type = $("#com_type").val(); //le type de commision auquel on a affaire soit courtage ou gestion

                //input_montant_a_encaisser.val(0);
                input_solde_apres.val(solde_quittance);
                //$('#restant_total').val(montant_com_solde);
                if (com_type == "courtage") {
                    $(this).closest('tr').find('.restant_total').val(parseFloat($(this).data('reglement_montant_com_courtage')));
                } else {
                    $(this).closest('tr').find('.restant_total').val(parseFloat($(this).data('reglement_montant_com_gestion')));

                }

                if (this.checked) {
                    if (com_type == "courtage") {
                        input_montant_encaisse_court.removeAttr('readonly');
                        input_montant_encaisse_court.attr('required', true);
                        input_montant_encaisse_court.val(0);//montant_com_courtage;
                    } else {
                        input_montant_encaisse_gest.removeAttr('readonly');
                        input_montant_encaisse_gest.attr('required', true);
                        input_montant_encaisse_gest.val(0);//montant_com_gestion);
                    }
                    /// parade pour evider les doublons lors d'evenements
                    already_exist = $("#datatable_stock_input_com").find("#input_stock_" + $(this).val());
                    /// console.log(already_exist.length);
                    if (already_exist.length == 0) {
                        /** parade pour eviter que lors du filtre des lignes la somme ne soient plus calculer correctement, pour cela creer des champs dynamique de stockage qui seront calculer en lieu et place des chechbox de base **/
                        $("#datatable_stock_input_com").append("<input type='text' class='input_stock' id='input_stock_" + $(this).val() + "' data-reglement_id='" + parseFloat($(this).data('reglement_id')) + "' data-reglement_montant='" + parseFloat($(this).data('reglement_montant')) + "'  data-reglement_montant_com_courtage='" + parseFloat($(this).data('reglement_montant_com_courtage')) + "'  data-reglement_montant_com_gestion='" + parseFloat($(this).data('reglement_montant_com_gestion')) + "' data-reglement_montant_compagnie='" + parseFloat($(this).data('reglement_montant_compagnie')) + "'>");
                    }
                } else {
                    if (com_type == "courtage") {
                        input_montant_encaisse_court.attr('readonly', true);
                        input_montant_encaisse_court.removeAttr('required');
                        input_montant_encaisse_court.val(0);
                    } else {
                        input_montant_encaisse_gest.attr('readonly', true);
                        input_montant_encaisse_gest.removeAttr('required');
                        input_montant_encaisse_gest.val(0);
                    }
                    //console.log("a supprimer");
                    $("#input_stock_" + $(this).val()).remove();
                }

                calculer_montant_total_a_encaisser_court_gest(com_type);

            });

            //montant_a_regler
            $(document).on('change keyup', '.handle_calculer_montant_total_a_encaisser', function () {
                let com_type = $("#com_type").val(); //le type de commision auquel on a affaire soit courtage ou gestion
                //console.log($(this).closest('tr').find('td:first-child input').val());
                $("#input_stock_" + $(this).closest('tr').find('td:first-child input').val()).val($(this).val());
                //console.log(com_type)
                //console.log('handle_calculer_montant_total_a_encaisser');
                calculer_montant_total_a_encaisser_court_gest(com_type);

            });

            $(document).on('change keyup', '#debit_difference', function () {
                $('#credit_difference').val("");
                //calculer_montant_total_a_encaisser();
            });
            $(document).on('change keyup', '#credit_difference', function () {
                $('#debit_difference').val("");
                //calculer_montant_total_a_encaisser();
            });

            $(document).on('change', '#modal-encaissement-court-gest #compagnie', function () {
                let href_reglements_reverses = $(this).children('option:selected').data('href_reglements_reverses');
                let com_type = $("#com_type").val(); //le type de commision auquel on a affaire soit courtage ou gestion
                //console.log(com_type)

                //reinitialisons les points important pour la commission
                $("#datatable_stock_input_com").html("");
                $('#credit_difference').val("");
                $('#debit_difference').val("");

                calculer_montant_total_a_encaisser_court_gest(com_type);//vider les champs d'aperçu

                $('.montant_total_com').val(0);

                $('#btn_save_encaissement').attr('disabled', 'true');

                $('#box_reglements_reverses').load(href_reglements_reverses, function () {
                    $('#table_reglements_reverses').DataTable({
                        "language": {
                            "url": "../../static/admin_custom/js/French.json"
                        },
                        //order: [[0, 'desc']],
                        lengthMenu: [
                            [10, 25, 50, 100, -1], [10, 25, 50, 100, "Tout"]
                        ],
                        //sDom: "<'row'<'col-sm-6'>>t<'row'<'col-sm-6'><'col-sm-6'>>",
                        paging: false,
                        searching: true,
                        lengthChange: true,
                        bSort: false,
                        scrollX: true,
                    });
                });

            });


            //champs obligatoires variables selon le mode de règlement
            $(document).on('change', '#mode_reglement', function () {
                //si espèce
                if ($(this).val() == 1) {
                    $('#numero_piece').removeAttr('required');
                    $('#banque').removeAttr('required');
                    $('#libelle_numero_piece_required').html('');
                    $('#libelle_banque_required').html('');
                } else {
                    $('#numero_piece').attr('required', true);
                    //$('#banque').attr('required', true);
                    $('#libelle_numero_piece_required').html('*');
                    //$('#libelle_banque_required').html('*');
                }

            });

            //enregistrement
            $('#btn_save_encaissement').on('click', function () {

                let btn_save_encaissement = $(this);

                let formulaire = $('#form_add_encaissement_commission');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let com_type = $("#com_type").val(); //le type de commision auquel on a affaire soit courtage ou gestion

                if (formulaire.valid()) {

                    //désactiver le bouton Valider, pour empecher une double soumission du formulaire
                    btn_save_encaissement.attr('disabled', true);

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment effectuer cet encaissement ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu
                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formulaire.serialize(),
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {

                                                    $("#datatable_stock_input_com").html("");
                                                    window.open('../generer_bordereau_encaissement_compagnie_pdf/' + response.data.operation_id + '?type=' + com_type, '_blank');

                                                    location.reload();
                                                });


                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-encaissement-court-gest .alert .message').html(errors_list_to_display);

                                                $('#modal-encaissement-court-gest .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");

                                            btn_save_encaissement.removeAttr('disabled');

                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                    btn_save_encaissement.removeAttr('disabled');

                                }
                            }
                        ]
                    });
                    //fin demande confirmation


                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');

                    btn_save_encaissement.removeAttr('disabled');

                }

            });

        });

    });


    function calculer_montant_total_a_encaisser_court_gest(com_type) {

        let montant_total_reglements_coches = 0;
        let montant_total_a_regler_compagnie = 0;
        let montant_total_com_gestion = 0;
        let montant_total_com_courtage = 0;
        let montant_total_a_encaisser = 0;
        let montant_solde = 0;
        let difference_match = false;
        let erreur_difference = false;


        let credit_difference = $('#credit_difference').val().replaceAll(" ", "");
        credit_difference = credit_difference === "" || isNaN(credit_difference) ? 0 : parseFloat(credit_difference);
        let debit_difference = parseFloat($('#debit_difference').val().replaceAll(" ", ""));
        debit_difference = debit_difference === "" || isNaN(debit_difference) ? 0 : parseFloat(debit_difference);
        let text_compte_difference = $('#compte_difference option:selected').text();
        let is_perte_compte_difference = (text_compte_difference.indexOf("6511000") >= 0)
        console.log(is_perte_compte_difference);

        $('.input_stock').each(function (element) {

            let montant_reglement = parseFloat($("#input_stock_" + $(this).data('reglement_id')).data('reglement_montant'));
            let montant_compagnie = parseFloat($("#input_stock_" + $(this).data('reglement_id')).data('reglement_montant_compagnie'));
            if (com_type == "courtage") {
                let montant_com_courtage = parseFloat($("#input_stock_" + $(this).data('reglement_id')).data('reglement_montant_com_courtage'));
                let montant_a_encaisser_court = parseFloat($("#input_stock_" + $(this).data('reglement_id')).val().replaceAll(" ", ""));
                montant_a_encaisser_court = montant_a_encaisser_court === "" || isNaN(montant_a_encaisser_court) ? 0 : parseFloat(montant_a_encaisser_court);
                montant_total_com_courtage = montant_total_com_courtage + montant_a_encaisser_court;
                montant_total_a_encaisser = montant_total_com_courtage;
                difference = montant_com_courtage - montant_a_encaisser_court;
                if (montant_com_courtage < montant_a_encaisser_court) {
                    erreur_difference = false; //true; car peut encaisser un montant superieur
                }
            }
            else {
                let montant_com_gestion = parseFloat($("#input_stock_" + $(this).data('reglement_id')).data('reglement_montant_com_gestion'));
                let montant_a_encaisser_gest = parseFloat($("#input_stock_" + $(this).data('reglement_id')).val().replaceAll(" ", ""));
                montant_a_encaisser_gest = montant_a_encaisser_gest === "" || isNaN(montant_a_encaisser_gest) ? 0 : parseFloat(montant_a_encaisser_gest);
                montant_total_com_gestion = montant_total_com_gestion + montant_a_encaisser_gest;
                montant_total_a_encaisser = montant_total_com_gestion;
                difference = montant_com_gestion - montant_a_encaisser_gest;
                if (montant_com_gestion < montant_a_encaisser_gest) {
                    erreur_difference = false; //true; car peut encaisser un montant superieur
                }
            }

            let montant_a_encaisser = parseFloat($("#checkbox_quittance_a_encaisser_" + $(this).data('reglement_id')).closest('tr').find('.montant_a_encaisser').val());
            //montant_a_encaisser = montant_a_encaisser === "" ? 0 : parseFloat(montant_a_encaisser);


            montant_total_reglements_coches = montant_total_reglements_coches + montant_reglement;
            montant_total_a_regler_compagnie = montant_total_a_regler_compagnie + montant_compagnie;
            //montant_total_a_encaisser       = montant_total_a_encaisser + montant_a_encaisser;

            $("#checkbox_quittance_a_encaisser_" + $(this).data('reglement_id')).closest('tr').find('.restant_total').val(difference);

            if (debit_difference == difference && difference_match == false && difference > 0 && ((difference < 3000 && is_perte_compte_difference==true) || (is_perte_compte_difference==false))) {
                difference_match = true;
                if (debit_difference == difference && difference > 0) {
                    $("#checkbox_quittance_a_encaisser_" + $(this).data('reglement_id')).closest('tr').find('.restant_total').val(difference - debit_difference);
                    $("#checkbox_quittance_a_encaisser_" + $(this).data('reglement_id')).closest('tr').find('.handle_calculer_montant_total_a_encaisser').removeAttr('required');
                }
            }

            if (credit_difference == (-1 * difference) && difference_match == false && credit_difference > 0) {
                difference_match = true;
                if (credit_difference == (-1 * difference)) {
                    $("#checkbox_quittance_a_encaisser_" + $(this).data('reglement_id')).closest('tr').find('.restant_total').val(difference + credit_difference);
                    $("#checkbox_quittance_a_encaisser_" + $(this).data('reglement_id')).closest('tr').find('.handle_calculer_montant_total_a_encaisser').removeAttr('required');
                }
            }

            if (difference < 0) {
                erreur_difference = false; //true; car peut encaisser un montant superieur
            }

            montant_solde = montant_solde + difference;

            /*
            difference = montant_com_courtage-montant_a_encaisser_court+montant_com_gestion-montant_a_encaisser_gest
            if (difference > 0 && difference < 3000){
                $('#debit_difference').val(difference);
                $('#credit_difference').val("");
                $('#credit_difference').attr('readonly','true');
            }
            */

        });

        $('.montant_total_reglements_coches').val(montant_total_reglements_coches);
        $('.montant_total_a_regler_compagnie').val(montant_total_a_regler_compagnie);
        if (com_type == "courtage") {
            $('.montant_total_com_gestion').val(montant_total_com_gestion);
        } else {
            $('.montant_total_com_courtage').val(montant_total_com_courtage);
        }
        // $('.montant_total_com').val(montant_total_a_encaisser + credit_difference);
        $('.montant_total_com').val(montant_total_a_encaisser);

        if (montant_total_a_encaisser != 0 || (montant_total_a_encaisser == 0 && debit_difference > 0) || (montant_total_a_encaisser == 0 && credit_difference > 0)) {
            $('#btn_save_encaissement').removeAttr('disabled');
            console.log("enabled");
        } else {
            $('#btn_save_encaissement').attr('disabled', 'true');
            console.log("disabled 1");
        }

        if (((credit_difference > 0 || debit_difference > 0) && $('#compte_difference').val() == "")
            || (debit_difference > 3000 && is_perte_compte_difference==true)
            || (debit_difference > 0 && difference_match == false)
            || (credit_difference > 0 && difference_match == false)
            || ($('#compte_difference').val() != "" && debit_difference == 0 && credit_difference == 0)
            //|| (montant_solde > 0 && credit_difference > 0)
            || erreur_difference == true) {
            $('#btn_save_encaissement').attr('disabled', 'true');
            console.log("disabled 2");
        }

    }


    //********* FIN FAIRE UN ENCAISSEMENT COURTAGE / GESTION ***********//

    //********* FAIRE UN REGLEMENT COMPAGNIE ***********//

    $(".btnOpenDialogDetailCompagnieEncaissementReglement").on('dblclick', function () {

        $(".btnOpenDialogDetailCompagnieEncaissementReglement").removeClass('tr_selected');
        $(this).addClass('tr_selected');
        let compagnie = $(this).data('compagnie');
        $("#datatable_stock_input_com").html("");
        $("#btnOpenDialogAddReglementCompagnie").trigger("click");

    });

    $("#btnOpenDialogAddReglementCompagnie").on('click', function () {

        let model_name = $(this).data('model_name');
        let modal_title = $(this).data('modal_title');
        let href = $(this).data('href');
        $("#datatable_stock_input_reg").html("");

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-reglement_compagnie').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-reglement_compagnie').find('.modal-title').text(modal_title);
            $('#modal-reglement_compagnie').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-reglement_compagnie').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-reglement_compagnie').modal();

            $('#modal-reglement_compagnie').on('shown.bs.modal', function () {
                compagnie = typeof $('.tr_selected') !== 'undefined' ? $('.tr_selected').data('compagnie') : "";
                if (compagnie && compagnie != "") {
                    $('#modal-reglement_compagnie #compagnie option[value=' + compagnie + ']').attr('selected', 'selected');
                    $("#modal-reglement_compagnie #compagnie").trigger('change');
                }
            })

            $('.form-add_reglement_compagnie-select').select2();

            //
            $(document).on('change', '#modal-reglement_compagnie #compagnie', function () {

                $("#datatable_stock_input_reg").html("");
                let href_reglements_a_reverser = $(this).children('option:selected').data('href_reglements_a_reverser');

                calculer_montant_total_a_regler_compagnie();

                $('#box_reglements_a_reverser_compagnie').load(href_reglements_a_reverser, function () {
                    $('#table_reglements_a_reverser_compagnie').DataTable({
                        "language": {
                            "url": "../../static/admin_custom/js/French.json"
                        },
                        //order: [[0, 'desc']],
                        lengthMenu: [
                            [10, 25, 50, 100, -1], [10, 25, 50, 100, "Tout"]
                        ],
                        //sDom: "<'row'<'col-sm-6'>>t<'row'<'col-sm-6'><'col-sm-6'>>",
                        paging: true,
                        searching: true,
                        lengthChange: true,
                        bSort: false,
                    });
                });

            });

            //gestion des saisies des montants à regler
            $(document).on('click', '.checkbox_quittance_a_regler', function () {

                /** parade pour eviter que lors du filtre des lignes la somme ne soient plus calculer correctement, pour cela creer des champs dynamique de stockage qui seront calculer en lieu et place des chechbox de base **/
                if ($(this).is(":checked")) {
                    /// parade pour evider les doublons lors d'evenements
                    already_exist = $("#datatable_stock_input_reg").find("#input_stock_" + $(this).val());
                    /// console.log(already_exist.length);
                    if (already_exist.length == 0) {
                        /** parade pour eviter que lors du filtre des lignes la somme ne soient plus calculer correctement, pour cela creer des champs dynamique de stockage qui seront calculer en lieu et place des chechbox de base **/
                        $("#datatable_stock_input_reg").append("<input type='text' class='input_stock' id='input_stock_" + $(this).val() + "' value='" + $(this).val() + "' data-reglement_montant='" + parseFloat($(this).data('reglement_montant')) + "'  data-reglement_montant_com_courtage='" + parseFloat($(this).data('reglement_montant_com_courtage')) + "'  data-reglement_montant_com_gestion='" + parseFloat($(this).data('reglement_montant_com_gestion')) + "' data-reglement_montant_compagnie='" + parseFloat($(this).data('reglement_montant_compagnie')) + "'>");
                    }
                }
                else {
                    //console.log("a supprimer");
                    $("#input_stock_" + $(this).val()).remove();
                }

                calculer_montant_total_a_regler_compagnie();

            });


            //champs obligatoires variables selon le mode de règlement
            $(document).on('change', '#mode_reglement', function () {
                //si espèce
                /*if($(this).val() == 1){
                    $('#numero_piece').removeAttr('required');
                    $('#banque').removeAttr('required');
                    $('#libelle_numero_piece_required').html('');
                    $('#libelle_banque_required').html('');
                }else{
                    $('#numero_piece').attr('required', true);
                    $('#banque').attr('required', true);
                    $('#libelle_numero_piece_required').html('*');
                    $('#libelle_banque_required').html('*');
                }*/

            });

            //enregistrement
            $('#btn_save_reglement_compagnie').on('click', function () {

                let btn_save_reglement_compagnie = $(this);

                let formulaire = $('#form_add_reglement_compagnie');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                if (formulaire.valid()) {

                    //désactiver le bouton Valider, pour empecher une double soumission du formulaire
                    btn_save_reglement_compagnie.attr('disabled', true);

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment effectuer ce reglement compagnie ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu
                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formulaire.serialize(),
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    //rediriger pour afficher le bordereau de reglement compagnie en pdf
                                                    operation_id = response.data.operation_id;

                                                    window.open('../generer_bordereau_reglement_compagnie_pdf/' + operation_id, '_blank');

                                                    location.reload();

                                                });


                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-reglement_compagnie .alert .message').html(errors_list_to_display);

                                                $('#modal-reglement_compagnie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");

                                            btn_save_reglement_compagnie.removeAttr('disabled');

                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                    btn_save_reglement_compagnie.removeAttr('disabled');

                                }
                            }
                        ]
                    });
                    //fin demande confirmation


                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');

                    btn_save_reglement_compagnie.removeAttr('disabled');

                }

            });

        });

    });

    //********* FIN FAIRE UN REGLEMENT COMPAGNIE ***********//

     //********* FAIRE UN ENCAISSEMENT DE COMMISSION RETROCESSION APPORTEUR ***********//

    // Double clic sur une ligne d'apporteur pour charger la modale
    $(".btnOpenDialogDetailApporteurEncaissementRetrocession").on('dblclick', function () {
        $(".btnOpenDialogDetailApporteurEncaissementRetrocession").removeClass('tr_selected');
        $(this).addClass('tr_selected');
        $("#datatable_stock_input_com").html("");
        $("#btnOpenDialogAddEncaissementRetrocession").trigger("click");
    });

    // Ouverture de la modale
    $("#btnOpenDialogAddEncaissementRetrocession").on('click', function () {
        let model_name = $(this).data('model_name');
        let modal_title = $(this).data('modal_title');
        let href = $(this).data('href');

        $('#olea_std_dialog_box').load(href, function () {
            AppliquerMaskSaisie();

            const modal = $('#modal-encaissement-retrocession');
            modal.attr('data-backdrop', 'static').attr('data-keyboard', false);
            modal.find('.modal-title').text(modal_title);
            modal.find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            modal.find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');
            modal.modal();

            modal.on('shown.bs.modal', function () {
                let apporteur = $('.tr_selected').data('apporteur') || "";
                if (apporteur) {
                    $("#apporteur option[value='" + apporteur + "']").attr('selected', 'selected');
                    $("#apporteur").trigger('change');
                }
            });

            //enregistrement
            $('#btn_save_retrocession_apporteur').on('click', function () {

                let btn_save_retrocession_apporteur = $(this);

                let formulaire = $('#form_add_encaissement_retrocession');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                if (formulaire.valid()) {

                    //désactiver le bouton Valider, pour empecher une double soumission du formulaire
                    btn_save_retrocession_apporteur.attr('disabled', true);

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment effectuer cet encaissement de retrocession apporteur ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu
                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formulaire.serialize(),
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {

                                                    $("#datatable_stock_input_com").html("");
                                                    window.open('../generer_bordereau_encaissement_apporteur_pdf/' + response.data.operation_id, '_blank');

                                                    location.reload();
                                                });


                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-encaissement-retrocession .alert .message').html(errors_list_to_display);

                                                $('#modal-encaissement-retrocession .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");

                                            btn_save_encaissement.removeAttr('disabled');

                                        }

                                    });

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                    btn_save_encaissement.removeAttr('disabled');

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');

                    btn_save_encaissement.removeAttr('disabled');

                }

            });
        });
    });

    // Gestion du changement d'apporteur
    $(document).on('change', '#modal-encaissement-retrocession #apporteur', function () {
        const select = $(this);
        const selectedValue = select.val();
        const href_reglements_reverses = select.children('option:selected').data('href_reglements_reverses');

        $("#datatable_stock_input_com").html("");
        $('.montant_total_retrocession').val("0");
        $('#btn_save_retrocession_apporteur').attr('disabled', true);

        if (!selectedValue) {
            $('#box_reglements_reverses').html("");
            return;
        }

        $('#box_reglements_reverses').load(href_reglements_reverses, function () {
            $('#table_reglements_reverses').DataTable({
                "language": { "url": "../../static/admin_custom/js/French.json" },
                lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Tout"]],
                paging: false,
                searching: true,
                lengthChange: true,
                bSort: false,
                scrollX: true,
            });
        });
    });

    // Clic sur une case à cocher pour activer ou désactiver un champ montant
    $(document).on('click', '.checkbox_quittance_a_encaisser_retro_apporteur', function () {
        const checkbox = $(this);
        const tr = checkbox.closest('tr');
        const reglement_id = checkbox.data('reglement_id');
        const restant_input = tr.find('.restant_total');
        const montant_restant = parseFloat(restant_input.val().replaceAll(' ', '')) || 0;

        restant_input.attr('data-restant_ref', montant_restant);

        //input_montant.removeClass('input-error');
        restant_input.removeClass('input-error').next('.text-error').remove();

        if (checkbox.is(':checked')) {
            if (!$('#input_stock_' + reglement_id).length) {
                $("#datatable_stock_input_com").append(
                    `<input type='text' class='input_stock' id='input_stock_${reglement_id}'
                        data-reglement_id='${reglement_id}'
                        data-reglement_montant='${montant_restant}'
                        data-reglement_montant_apporteur='${checkbox.data('reglement_montant_retrocession_apporteur')}'
                        value='${checkbox.data('reglement_montant_retrocession_apporteur')}'>`
                );
            }
        } else {
            $('#input_stock_' + reglement_id).remove();
            restant_input.val(restant_input.attr('data-restant_ref')).removeClass('input-error').next('.text-error').remove();
        }

        calculer_montant_total_a_encaisser_retrocession();
    });

    // Mise à jour dynamique des montants
    $(document).on('keyup change', '.handle_calculer_montant_total_a_encaisser', function () {
        const tr = $(this).closest('tr');
        const checkbox = tr.find('td:first-child input');
        const reglement_id = checkbox.val();
        const montant_saisi = parseFloat($(this).val().replaceAll(' ', '')) || 0;
        const restant_input = tr.find('.restant_total');
        const montant_restant = parseFloat(restant_input.attr('data-restant_ref')) || 0;

        const input = $(this);
        let erreur = false;

        if (montant_saisi > montant_restant) {
            input.addClass('input-error');
            restant_input.addClass('input-error');
            erreur = true;
        } else {
            input.removeClass('input-error');
            restant_input.removeClass('input-error');
            restant_input.next('.text-error').remove();
        }

        $("#input_stock_" + reglement_id).val($(this).val());
        restant_input.val((montant_restant - montant_saisi).toFixed(2));

        calculer_montant_total_a_encaisser_retrocession();
    });

    // Fonction de calcul total
    function calculer_montant_total_a_encaisser_retrocession() {
        let total_courtage = 0, total_apporteur = 0, total_general = 0;
        let hasError = false;

        $('.input_stock').each(function () {
            const stock = $(this);
            const montant_courtage = parseFloat(stock.data('reglement_montant')) || 0;
            const montant_apporteur = parseFloat(stock.data('reglement_montant_apporteur')) || 0;

            total_courtage += montant_courtage;
            total_apporteur += montant_apporteur;
            total_general += montant_courtage;
        });

        console.log("total_courtage: " + total_courtage);
        console.log("total_apporteur: " + total_apporteur);
        console.log("total_general: " + total_general);


        $('.montant_total_reglements_coches').val(total_courtage);
        $('.montant_total_a_regler_apporteur').val(total_apporteur);
        $('.montant_total_retrocession').val(total_general);

        if (total_general > 0 && !hasError && $('.input-error').length === 0) {
            $('#btn_save_retrocession_apporteur').removeAttr('disabled');
        } else {
            $('#btn_save_retrocession_apporteur').attr('disabled', true);
        }
    }
    //********* FIN FAIRE UN ENCAISSEMENT RETROCESSION APPORTEUR ***********//



    //********** FAIRE UN REGLEMENT BORDEREAU D"ORDONNANCEMENT */
    $("#btnOpenDialogAddReglementBordereau").on('click', function () {

        let model_name = $(this).data('model_name');
        let modal_title = $(this).data('modal_title');
        let href = $(this).data('href');

        //alert(href);

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-reglement_ordonnancement').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-reglement_ordonnancement').find('.modal-title').text(modal_title);
            $('#modal-reglement_ordonnancement').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-reglement_ordonnancement').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-reglement_ordonnancement').modal();


            //enregistrement
            $('#btn_save_reglement_ordonnancement').on('click', function () {

                let btn_save_reglement_ordonnancement = $(this);

                let formulaire = $('#form_add_reglement_ordonnancement');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                if (formulaire.valid()) {

                    //désactiver le bouton Valider, pour empecher une double soumission du formulaire
                    btn_save_reglement_ordonnancement.attr('disabled', true);

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment éffectuer ce règlement de paiement ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu
                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formulaire.serialize(),
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    //rediriger pour afficher le bordereau de reglement compagnie en pdf
                                                    operation_id = response.data.operation_id;
                                                    //alert("operation_id = response.data.operation_id " + operation_id)

                                                    location.href = 'comptabilite/generer_bordereau_reglement_ordonnancement_pdf/' + operation_id;
                                                    ///alert(location_href);

                                                    location.reload();

                                                });


                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-reglement_ordonnancement .alert .message').html(errors_list_to_display);

                                                $('#modal-reglement_ordonnancement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");

                                            btn_save_reglement_ordonnancement.removeAttr('disabled');

                                        }

                                    });

                                    //fin confirmation obtenue
                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                    btn_save_reglement_ordonnancement.removeAttr('disabled');

                                }
                            }
                        ]
                    });
                    //fin demande confirmation

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');

                    btn_save_reglement_ordonnancement.removeAttr('disabled');

                }


            });

        });

    });


    function calculer_montant_total_a_regler_compagnie() {

        let montant_total_reglements_coches = 0;
        let montant_total_a_regler_compagnie = 0;
        let montant_total_com_gestion = 0;
        let montant_total_com_courtage = 0;

        $('.input_stock').each(function (element) { // on parcours les champs hidden qui stock les valeurs stocké lors du check des case à cocher

            let montant_reglement = parseFloat($("#input_stock_" + $(this).val()).data('reglement_montant'));
            let montant_compagnie = parseFloat($("#input_stock_" + $(this).val()).data('reglement_montant_compagnie'));
            let montant_com_courtage = parseFloat($("#input_stock_" + $(this).val()).data('reglement_montant_com_courtage'));

            montant_total_reglements_coches = montant_total_reglements_coches + montant_reglement;
            montant_total_a_regler_compagnie = montant_total_a_regler_compagnie + montant_compagnie;
            montant_total_com_courtage = montant_total_com_courtage + montant_com_courtage;

            console.log('montant_total_reglements_coches : ',montant_total_reglements_coches);
            console.log('montant_total_a_regler_compagnie : ',montant_total_a_regler_compagnie);
            console.log('montant_total_com_gestion : ',montant_total_com_gestion);
            console.log('montant_total_com_courtage : ',montant_total_com_courtage);

        });

        $('.montant_total_reglements_coches').val(montant_total_reglements_coches);
        $('.montant_total_a_regler_compagnie').val(montant_total_a_regler_compagnie);
        $('.montant_total_com_gestion').val(montant_total_com_gestion);
        $('.montant_total_com_courtage').val(montant_total_com_courtage);
        $('.montant_total_com').val(montant_total_com_gestion + montant_total_com_courtage);

        if (montant_total_a_regler_compagnie > 0) {
            $('#btn_save_reglement_compagnie').removeAttr('disabled');
        } else {
            $('#btn_save_reglement_compagnie').attr('disabled', 'true');
        }

    }

    //********* FIN FAIRE UN REGLEMENT COMPAGNIE ***********//


    //********* FAIRE UNE EXPORTATION DES QUITTANCES VIA LA POLICE ***********//
    $("#btnOpenDialogExporterQuittance").on('click', function () {

        let model_name = $(this).data('model_name');
        let modal_title = $(this).data('modal_title');
        let href = $(this).data('href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-exporter_quittance').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-exporter_quittance').find('.modal-title').text(modal_title);
            $('#modal-exporter_quittance').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-exporter_quittance').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-exporter_quittance').modal();

            //enregistrement
            $('#btn_save_exporter_quittance').on('click', function () {

                let btn_save_exporter_quittance = $(this);

                let formulaire = $('#modal_form_exporter_quittance');
                let href = formulaire.attr('action');

                let periode_debut = $('#periode_debut').val();
                let periode_fin = $('#periode_fin').val();

                if (periode_debut && !periode_fin) {
                    notifyWarning('La période fin est obligatoire lorsque la période début est renseignée.');
                    return;
                }

                if (new Date(periode_debut) > new Date(periode_fin)) {
                    notifyWarning('La période début doit être antérieure ou égale à la période fin.');
                    return;
                }

                $.validator.setDefaults({ ignore: [] });

                if (formulaire.valid()) {

                    //désactiver le bouton Valider, pour empecher une double soumission du formulaire
                    btn_save_exporter_quittance.attr('disabled', true);

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment effectuer cette exportation ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu
                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formulaire.serialize(),
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    window.open(response.data.pdf_url, '_blank');
                                                    location.reload();
                                                });

                                            } else {

                                                notifyWarning(response.message, function () {
                                                    location.reload();
                                                });

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de le l'exportation");

                                            btn_save_exporter_quittance.removeAttr('disabled');

                                        }

                                    });
                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                    btn_save_exporter_quittance.removeAttr('disabled');

                                }
                            }
                        ]
                    });
                    //fin demande confirmation

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');

                    btn_save_exporter_quittance.removeAttr('disabled');

                }

            });

        });

    });
    //********* FIN FAIRE UNE EXPORTATION DES QUITTANCES VIA LA POLICE ***********//

    //GESTION SINISTRE

    //ouverture de la boite de dialog
    $('.modal-sinistre').on('shown.bs.modal', function () {
        let formulaire = $(this).find('form');
        formulaire.trigger('reset');
        $('#acte').trigger('reset');
        hideAndEmptyOrShowSibbling('varAlimentSinistreAutre', formulaire, 'hide');
    })
    .on('hidden.bs.modal', function () {
        let formulaire = $(this).find('form');
        formulaire.trigger('reset');
        $('#acte').trigger('reset');
        hideAndEmptyOrShowSibbling('varAlimentSinistreAutre', formulaire, 'hide');
    });

    //recherche d'un sinistré
    $(document).on('click', '.btnSearchAlimentSinistreAutre', function () {
        performSearchAliment($(this));
    });


    function hideAndEmptyOrShowSibbling(classDependance, form, etat) {

        form.find("#current_searched_aliment_id").val("");
        $("." + classDependance + "").hide();
        $("." + classDependance + " input:not(.not_resetable)").val("");
        if (etat == "show") {
            $("." + classDependance + "").show();
        }
    }

    function is_specials_keys(keyCode) {
        return (keyCode == 8 || keyCode == 9 || keyCode == 46 || keyCode == 37 || keyCode == 39);
    }

    //soumission du formulaire de sinistre
    function validateSinistreDates() {
        // Récupérer les valeurs des champs de date
        let date_survenance = $('#date_survenance').val();
        let date_declaration = $('#date_declaration').val();
        let date_ouverture = $('#date_ouverture').val();
        let date_reouverture = $('#date_reouverture').val();
        let date_cloture = $('#date_cloture').val();

        // Convertir les chaînes de dates en objets Date pour comparaison
        let d_survenance = date_survenance ? new Date(date_survenance) : null;
        let d_declaration = date_declaration ? new Date(date_declaration) : null;
        let d_ouverture = date_ouverture ? new Date(date_ouverture) : null;
        let d_reouverture = date_reouverture ? new Date(date_reouverture) : null;
        let d_cloture = date_cloture ? new Date(date_cloture) : null;

        // Fonction pour vérifier si une date est valide
        function isValidDate(d) {
            return d instanceof Date && !isNaN(d);
        }

        // Validation des dates
        let errors = [];

        // Vérifier que les dates remplies sont valides
        if (date_survenance && !isValidDate(d_survenance)) {
            errors.push("La date de survenance est invalide.");
        }
        if (date_declaration && !isValidDate(d_declaration)) {
            errors.push("La date de déclaration est invalide.");
        }
        if (date_ouverture && !isValidDate(d_ouverture)) {
            errors.push("La date d'ouverture est invalide.");
        }
        if (date_reouverture && !isValidDate(d_reouverture)) {
            errors.push("La date de réouverture est invalide.");
        }
        if (date_cloture && !isValidDate(d_cloture)) {
            errors.push("La date de clôture est invalide.");
        }

        // Vérifier l'ordre chronologique des dates si elles sont remplies
        if (isValidDate(d_survenance) && isValidDate(d_declaration) && d_survenance > d_declaration) {
            errors.push("La date de survenance doit être antérieure ou égale à la date de déclaration.");
        }
        if (isValidDate(d_declaration) && isValidDate(d_ouverture) && d_declaration > d_ouverture) {
            errors.push("La date de déclaration doit être antérieure ou égale à la date d'ouverture.");
        }
        if (isValidDate(d_ouverture) && isValidDate(d_reouverture) && d_ouverture > d_reouverture) {
            errors.push("La date d'ouverture doit être antérieure ou égale à la date de réouverture.");
        }
        if (isValidDate(d_reouverture) && isValidDate(d_cloture) && d_reouverture > d_cloture) {
            errors.push("La date de réouverture doit être antérieure ou égale à la date de clôture.");
        }
        if (isValidDate(d_ouverture) && isValidDate(d_cloture) && d_ouverture > d_cloture) {
            errors.push("La date d'ouverture doit être antérieure ou égale à la date de clôture.");
        }

        // Si des erreurs sont détectées
        if (errors.length > 0) {
            notifyWarning(errors.join("\n"));
            return false;
        }

        return true;
    }

    function buildFormData(formulaire) {
        let formData = new FormData();

        // Ajouter les données du formulaire classique
        let data_serialized = formulaire.serialize();
        $.each(data_serialized.split('&'), function (index, elem) {
            let vals = elem.split('=');
            let key = vals[0];
            let valeur = decodeURIComponent(vals[1].replace(/\+/g, ' '));
            formData.append(key, valeur);
        });

        // Ajouter les données du tableau des provisions
        $("#table_provision_sinistre input").each(function () {
            let key = $(this).attr("name");
            let valeur = $(this).val();
            if (key) {
                formData.append(key, valeur);
            }
        });

        return formData;
    }

    $(document).on('click', "#btn_save_sinistre_gestionnaire", function () {
        let formulaire = $('#form_add_sinistre_gestionnaire');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });
        let formData = buildFormData(formulaire);

        if (formulaire.valid()) {
            // Vérifier les dates avant de désactiver le bouton
            if (!validateSinistreDates()) {
                return;
            }

            // Récupération des dates
            let date_du_jour = $('#date_du_jour').val();
            let date_fin_effet = $('#date_fin_effet').val();

            // Construction des données du formulaire
            let data_serialized = formulaire.serialize();
            $.each(data_serialized.split('&'), function (index, elem) {
                let vals = elem.split('=');
                let key = vals[0];
                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));
                formData.append(key, valeur);
            });


            // Affichage du noty de confirmation
            noty({
                text: "Voulez-vous vraiment enregistrer ce sinistre ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'VALIDER', onClick: function ($noty) {
                            $noty.close();
                            envoyerFormulaireAjax(formulaire, href, formData);
                        }
                    },
                    {
                        addClass: 'btn btn-secondary', text: 'ANNULER', onClick: function ($noty) {
                            $noty.close();
                        }
                    }
                ]
            });

        } else {
            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');
            let validator = formulaire.validate();
            $.each(validator.errorMap, function (index, value) {
                console.log('Id: ' + index + ' Message: ' + value);
            });
            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }
    });

    function envoyerFormulaireAjax(formulaire, href, formData) {
        $.ajax({
            type: 'post',
            url: href,
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.statut == 1) {
                    resetFields('#' + formulaire.attr('id'));
                    notifySuccess(response.message, function () {
                        window.location.href = response.url_return;
                    });
                }
                if (response.statut == 0) {
                    notifyWarning(response.message, function () {
                        //location.reload();
                    });
                }
                else {
                    let errors = response.errors;
                    let errors_list_to_display = '';
                    for (field in errors) {
                        errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                    }
                    $('#formulaire_page .alert .message').html(errors_list_to_display);
                    $('#formulaire_page .alert ').fadeTo(2000, 500).slideUp(500, function () {
                        $(this).slideUp(500);
                    }).removeClass('alert-success').addClass('alert-warning');
                }
            },
            error: function (request, status, error) {
                notifyWarning("Erreur lors de l'enregistrement");
            }
        });
    }

    $(document).on('click', "#btn_update_sinistre_gestionnaire", function () {
        let formulaire = $('#form_update_sinistre_gestionnaire');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });
        let formData = new FormData(formulaire[0]);

        if (formulaire.valid()) {
            // Vérifier les dates avant de désactiver le bouton
            if (!validateSinistreDates()) {
                return;
            }

            // Construction des données du formulaire
            let data_serialized = formulaire.serialize();
            $.each(data_serialized.split('&'), function (index, elem) {
                let vals = elem.split('=');
                let key = vals[0];
                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));
                formData.append(key, valeur);
            });

            // Affichage du noty de confirmation
            noty({
                text: "Voulez-vous vraiment modifier ce sinistre ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'VALIDER', onClick: function ($noty) {
                            $noty.close();
                            envoyerFormulaireModificationAjax(formulaire, href, formData);
                        }
                    },
                    {
                        addClass: 'btn btn-secondary', text: 'ANNULER', onClick: function ($noty) {
                            $noty.close();
                        }
                    }
                ]
            });

        } else {
            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');
            let validator = formulaire.validate();
            $.each(validator.errorMap, function (index, value) {
                console.log('Id: ' + index + ' Message: ' + value);
            });
            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }
    });

    function envoyerFormulaireModificationAjax(formulaire, href, formData) {
        $.ajax({
            type: 'post',
            url: href,
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.statut == 1) {
                    resetFields('#' + formulaire.attr('id'));
                    notifySuccess(response.message, function () {
                        location.reload();
                    });
                }
                if (response.statut == 2) {
                    notifySuccess(response.message, function () {
                        window.location.href = response.url_return;
                    });
                }
                if (response.statut == 0) {
                    notifyWarning(response.message, function () {
                        //location.reload();
                    });
                }
                else {
                    let errors = response.errors;
                    let errors_list_to_display = '';
                    for (field in errors) {
                        errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                    }
                    $('#formulaire_update_page .alert .message').html(errors_list_to_display);
                    $('#formulaire_update_page .alert ').fadeTo(2000, 500).slideUp(500, function () {
                        $(this).slideUp(500);
                    }).removeClass('alert-success').addClass('alert-warning');
                }
            },
            error: function (request, status, error) {
                notifyWarning("Erreur lors de l'enregistrement");
            }
        });
    }


    //afficher le détail d'un sinistre
    $(document).on("click", ".btn-popup_details_sinistre", function (e) {
        e.preventDefault();

        href = $(this).data('href');

        $('#olea_std_dialog_box').load(href, function () {

            $('#modal-details_sinistre').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-details_sinistre').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            AppliquerMaskSaisie();

            //appliquer datatable
            $('#table_historique_acte').DataTable({
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"
                },
                order: [[0, 'asc']],
                paging: false,
                searching: false,
                lengthChange: false,
            });

            //
            $('#modal-details_sinistre').modal();

            //alert("opened details_sinistre");

        });

    });

    $('#modal-details_sinistre').on('shown.bs.modal', function () {
        //alert("opened");
    })

    // APPROUVER LA SELECTION D'UN ACTE
    $(document).on("click", "#btn_approuver_sinistre", function (e) {
        // e.preventDefault();
        //var buttonApprouver = document.getElementById('btn_approuver_sinistre');
        var buttonApprouver = $(this);


        sinistre_id = $(this).data("acte_id");
        let nombre_demande = $(this).data("nombre_demande");
        let nombre_accorde = $('#nombre_accorde').val();
        let motif_rejet = $('#detail_motif_modif').val();
        let date_sortie_accorde = $('#date_sortie_accorde').val();

        type_operation = $(this).data("type_operation");


        if (nombre_accorde && nombre_accorde < nombre_demande) {
            //        alert(nombre_demande);
            motif_rejet = $('#detail_motif_modif').val();

            //    alert(motif_rejet);
            if (motif_rejet.length < 1) {
                // ON ARRETE LE REJET
                return notifyWarning("Veuillez saisir le motif de la modification");
            }

        }

        if (true) {

            buttonApprouver.attr('disabled', true);

            let n = noty({
                text: 'Voulez-vous vraiment approuver cet acte ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();
                            buttonApprouver.removeAttr('disabled');
                        }
                    },
                    {
                        addClass: 'btn btn-primary', text: 'Approuver', onClick: function ($noty) {
                            $noty.close();
                            //confirmation obtenu

                            // Make the AJAX request
                            $.ajax({
                                url: '/sinistre/statuer_acte/',
                                method: 'POST', // or 'GET' depending on your needs
                                data: {
                                    sinistre_id: sinistre_id,
                                    type_operation: type_operation,
                                    nombre_accorde: nombre_accorde,
                                    motif_rejet: motif_rejet,
                                },
                                success: function (response) {
                                    // Handle the success response
                                    console.log(response);
                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            //location.reload();
                                            location.href = response.redirectto;
                                        });

                                    } else {
                                        notifyWarning(response.message);
                                        buttonApprouver.removeAttr('disabled');
                                    }
                                },
                                error: function (error) {
                                    // Handle the error
                                    console.error(error);
                                    notifyWarning("Erreur survenue à l'approbation de l'acte.");
                                    buttonApprouver.removeAttr('disabled');
                                }
                            });
                        }
                    }
                ]
            }
            );

        }
    });
    // FIN APPROUVER LA SELECTION D'UN ACTE


    // REJETER LA SELECTION D'UN ACTE
    $(document).on("click", "#btn_rejeter_sinistre_un", function (e) {
        // e.preventDefault();
        //var buttonRejeter = document.getElementById('btn_rejeter_sinistre_un');
        var buttonRejeter = $(this);

        sinistre_id = buttonRejeter.attr("data-acte_id");
        type_operation = buttonRejeter.attr("data-type_operation");
        motif_rejet = $('#detail_motif_rejet').val();

        //    alert(motif_rejet);
        if (motif_rejet.length < 1) {
            // ON ARRETE LE REJET
            return notifyWarning("Veuillez saisir le motif du rejet");
        }

        buttonRejeter.attr('disabled', true);
        // Make the AJAX request
        $.ajax({
            url: '/sinistre/statuer_acte/',
            method: 'POST', // or 'GET' depending on your needs
            data: {
                sinistre_id: sinistre_id,
                type_operation: type_operation,
                motif_rejet: motif_rejet,
            },
            success: function (response) {
                // Handle the success response
                console.log(response);
                if (response.statut == 1) {

                    notifySuccess(response.message, function () {
                        //location.reload();
                        location.href = response.redirectto;
                    });

                } else {
                    notifyWarning("Erreur lors de l'approbation de l'acte");
                    buttonRejeter.removeAttr("disabled");
                }
            },
            error: function (error) {
                // Handle the error
                console.error(error);
                notifyWarning("Erreur survenue à l'approbation de l'acte.");
                buttonRejeter.removeAttr("disabled");
            }
        });

    });
    // FIN REJETER LA SELECTION D'UN ACTE

    //FIN GESTION SINISTRE

    //******************** GLOBALS ********************//

    //suppression de sinistre
    $(document).on("click", ".btn_supprimer_sinistre", function (e) {
        let sinistre_id = $(this).data("sinistre_id");
        let href = $(this).data("href");
        let libelle = $(this).data("libelle");

        let n = noty({
            text: 'Voulez-vous vraiment supprimer ' + libelle + ' ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //confirmation obtenu
                        $.ajax({
                            type: 'post',
                            url: href,
                            data: { sinistre_id: sinistre_id },
                            success: function (response) {

                                if (response.statut == 1) {

                                    notifySuccess(response.message, function () {
                                        location.reload();
                                    });

                                } else {
                                    notifyWarning(response.response);
                                }

                            },
                            error: function (request, status, error) {

                                notifyWarning("Erreur lors du traitement");
                            }

                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //confirmation refusée
                        $noty.close();

                    }
                }
            ]
        });
    });

    $(document).on("click", "#CloseTheBs", function (e) {

        dossier_sinistre_id = $(this).data("dossier_sinistre_id");
        href = $(this).data("close_dossier_sinistre_href");

        let n = noty({
            text: 'Voulez-vous cloturer cette feuille de soin ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                        $noty.close();

                        //confirmation obtenu
                        $.ajax({
                            type: 'post',
                            url: href,
                            data: { dossier_sinistre_id: dossier_sinistre_id },
                            success: function (response) {

                                if (response.statut == 1) {

                                    notifySuccess(response.message, function () {
                                        location.reload();

                                    });

                                } else {
                                    notifyWarning(response.response);
                                }

                            },
                            error: function (request, status, error) {

                                notifyWarning("Erreur lors du traitement");
                            }

                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //confirmation refusée
                        $noty.close();

                    }
                }
            ]
        });
    });

    //CONTROLE DU TRAITEMENT DE REMBOURSEMENT
    // Sélectionner/désélectionner | APPROUVER OU REJETER DES ACTES
    $(document).on("click", ".libelle_btnSelectAllRemboursements", function (e) {
        $("#btnSelectAllRemboursements").trigger("click");
    });

    $(document).on("click", "#btnSelectAllRemboursements", function (e) {
        var isChecked = $(this).prop('checked');
        $('#card_liste_remboursements .select-row:not(:disabled)').prop('checked', isChecked);

        let total_checked = $('#card_liste_remboursements .select-row:checked:not(:disabled)').length;
        if (total_checked > 0) {
            $('.btnActionDesRemboursements').removeAttr('disabled');
        } else {
            $('.btnActionDesRemboursements').attr('disabled', 'true');
        }

    });

    // Vérifier si toutes les lignes sont sélectionnées pour cocher le bouton "Sélectionner tout"
    $(document).on("change", "#card_liste_remboursements .select-row", function (e) {
        let cpt_selected = 0;

        let total_not_disabled = $('#card_liste_remboursements .select-row:not(:disabled)').length;
        let total_checked = $('#card_liste_remboursements .select-row:checked:not(:disabled)').length;

        // Cacher ou afficher le groupe de boutons en fonction de la sélection
        if (total_not_disabled === total_checked) {
            $('#btnSelectAllRemboursements').prop('checked', true);
        } else {
            $('#btnSelectAllRemboursements').prop('checked', false);
        }

        if (total_checked > 0) {
            $('.btnActionDesRemboursements').removeAttr('disabled');
        } else {
            $('.btnActionDesRemboursements').attr('disabled', 'disabled');
        }
    });

    //FIN DU TRAITEMENT DE REMBOURSEMENT

    $(document).on("keypress", "input[type=number]", function (evt) {
        var charCode = (evt.which) ? evt.which : evt.keyCode
        if (charCode > 31 && (charCode < 48 || charCode > 57))
            return false;

        return true;
    });


    function isNumberKey(evt) {
        var charCode = (evt.which) ? evt.which : evt.keyCode
        if (charCode > 31 && (charCode < 48 || charCode > 57))
            return false;

        return true;
    }


    function resetFields(formulaire) {

        //$(formulaire + " input[type=text]:not(.notreset)").val("");
        $(formulaire + " input:not(.notreset)").val("");
        $(formulaire + " input[type=number]:not(.notreset)").val("");
        $(formulaire + " input[type=date]:not(.notreset)").val("");
        $(formulaire + " input[type=email]:not(.notreset)").val("");
        $(formulaire + " select:not(.notreset)").prop('selectedIndex', 0);

    }


    function AppliquerMaskSaisie() {

        $('.money_field_avec_virgule').inputmask({
            alias: 'numeric',
            groupSeparator: ' ',
            autoGroup: true,
            digits: 2,
            digitsOptional: false,
            prefix: '',
            rightAlign: false,
            allowMinus: false,
            placeholder: '0',
            removeMaskOnSubmit: true
        });

        $('.money_field_only_positive').inputmask({
            alias: 'numeric',
            groupSeparator: ' ',
            autoGroup: true,
            digits: 0,
            digitsOptional: false,
            prefix: '',
            rightAlign: false,
            allowMinus: false,
            placeholder: '0',
            removeMaskOnSubmit: true
        });

        $('.float_field_only_positive').inputmask({
            alias: 'numeric',
            groupSeparator: '',
            autoGroup: true,
            digits: 2,
            digitsOptional: true,
            prefix: '',
            rightAlign: false,
            allowMinus: false,
            placeholder: '0.00',
            removeMaskOnSubmit: true,
            onBeforePaste: function (pastedValue) {
                // Convertir la valeur collée en format numérique
                return pastedValue.replace(',', '.'); // Remplacer la virgule par un point si nécessaire
            }
        });


        //appliquer le mask de saisie sur les champs montant
        Inputmask("currency", {
            prefix: "",
            groupSeparator: " ",//désactiver pour
            alias: "numeric",
            digits: 0,// nombre de caractère après la virgule
            onKeyDown: function (event) {
                var key = event.keyCode || event.charCode;

                // Empêcher la saisie du signe négatif
                if (key === 189 || key === 109) { // Les codes 189 et 109 correspondent au signe moins (-)
                    event.preventDefault();
                    return false;
                }
            }
        }).mask('.money_field');

        Inputmask("currency", {
            prefix: "",
            groupSeparator: " ",//désactiver pour
            alias: "numeric",
            digits: 0,// nombre de caractère après la virgule
            onKeyDown: function (event) {
                var key = event.keyCode || event.charCode;

                // Empêcher la saisie du signe négatif
                if (key === 189 || key === 109) { // Les codes 189 et 109 correspondent au signe moins (-)
                    event.preventDefault();
                    return false;
                }
            }
        }).mask('.total_autres_taxes');

        //appliquer le mask de saisie sur les champs montant
        Inputmask("currency", {
            prefix: "",
            groupSeparator: " ",//désactiver pour
            alias: "numeric",
            digits: 0,// nombre de caractère après la virgule
            onKeyDown: function (event) {
                var key = event.keyCode || event.charCode;

                // Empêcher la saisie du signe négatif
                /*
                if (key === 189 || key === 109) { // Les codes 189 et 109 correspondent au signe moins (-)
                    event.preventDefault();
                    return false;
                }
                */
            }
        }).mask('.money_field_negative');

    }
    AppliquerMaskSaisie();



    var my_noty;//variale global pour pouvoir le fermer de popup de l'extérieur
    function notifySuccess(message, fnCallback) {
        my_noty = noty({
            text: message,
            type: 'success',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'OK', onClick: function ($noty) {

                        if (typeof fnCallback === 'function') fnCallback();

                        $noty.close();
                    }
                }
            ]
        });
    }

    function notifyWarning(message, fnCallback) {
        if (my_noty) {
            my_noty.close();
        }

        my_noty = noty({
            text: message,
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'OK', onClick: function ($noty) {

                        if (typeof fnCallback === 'function') fnCallback();

                        $noty.close();
                    }
                }
            ]
        });

    }

    function notifyError(message, fnCallback) {
        my_noty = noty({
            text: message,
            type: 'error',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'OK', onClick: function ($noty) {

                        if (typeof fnCallback === 'function') fnCallback();

                        $noty.close();
                    }
                }
            ]
        });
    }


    function addInputAlphaNumValidation(inputSelector, errorId) {
        var previousValue = ""; // Déclarer previousValue en dehors de la fonction
        $(inputSelector).on("input", function () {
            var inputValue = $(this).val();
            // var alphanumericRegex = /^[a-zA-Z0-9]*$/;
            var alphanumericRegex = /^[a-zA-Z0-9\/\-_]*$/;
            var errorMessage = $("#" + errorId);

            if (!alphanumericRegex.test(inputValue)) {
                errorMessage.css("display", "block");
                $(this).val(previousValue);
                setTimeout(function () {
                    errorMessage.css("display", "none");
                }, 5000);
            } else {
                previousValue = inputValue;
                errorMessage.css("display", "none");
            }
        });
    }

    $(document).ready(function () {
        addInputAlphaNumValidation(".alpha_num_input", "error-message");
    });

    function apporteur_manage_type_personne_change() {
        let type_personne_id = parseInt($('#type_personne_id').val());

        switch (type_personne_id) {
            default:
            case 1: // personne physique
                $('#prenoms').closest('.form-group').show();
                $('#prenoms').attr('required', true);
                break;
            case 2: // personne morale
                $('#prenoms').closest('.form-group').hide();
                $('#prenoms').removeAttr('required');
                break;
        }
    }

    // Initialiser la gestion au chargement
    apporteur_manage_type_personne_change();

    // Attacher l'événement `change` au bon élément
    $(document).on('change', "#type_personne_id", function () {
        apporteur_manage_type_personne_change();
    });

    //Création d'un apporteur
    $(document).on('click', "#btn_save_apporteur", function () {

        let formulaire = $('#form_add_apporteur');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer ce client ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-apporteur .alert .message').html(errors_list_to_display);

                                        $('#modal-apporteur .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un apporteur
    $(document).on('click', '.btn_modifier_apporteur', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            apporteur_manage_type_personne_change();

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_apporteur').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_apporteur').find('.modal-title').text(modal_title);
            $('#modal-modification_apporteur').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_apporteur').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-modification_apporteur').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_apporteur").on('click', function () {

                let formulaire = $('#form_update_apporteur');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cet apporteur ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_apporteur .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_apporteur .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un apporteur
    $(document).on('click', '.btn_supprimer_apporteur', function () {
        let apporteur_id = $(this).data('apporteur_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cet apporteur ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { apporteur_id: apporteur_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });

    });

    //Création d'une banque
    $(document).on('click', "#btn_save_banque", function () {

        let formulaire = $('#form_add_banque');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer cette banque ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-banque .alert .message').html(errors_list_to_display);

                                        $('#modal-banque .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un banque
    $(document).on('click', '.btn_modifier_banque', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_banque').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_banque').find('.modal-title').text(modal_title);
            $('#modal-modification_banque').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_banque').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_banque').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_banque").on('click', function () {

                let formulaire = $('#form_update_banque');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cet banque ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_banque .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_banque .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un banque
    $(document).on('click', '.btn_supprimer_banque', function () {
        let banque_id = $(this).data('banque_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette banque ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { banque_id: banque_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une branche
    $(document).on('click', "#btn_save_branche", function () {

        let formulaire = $('#form_add_branche');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer cette branche ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-branche .alert .message').html(errors_list_to_display);

                                        $('#modal-branche .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un branche
    $(document).on('click', '.btn_modifier_branche', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_branche').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_branche').find('.modal-title').text(modal_title);
            $('#modal-modification_branche').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_branche').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_branche').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_branche").on('click', function () {

                let formulaire = $('#form_update_branche');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cet branche ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_branche .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_branche .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un branche
    $(document).on('click', '.btn_supprimer_branche', function () {
        let branche_id = $(this).data('branche_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette branche ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { branche_id: branche_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une compagnie
    $(document).on('click', "#btn_save_compagnie", function () {

        let formulaire = $('#form_add_compagnie');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer cet compagnie ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-compagnie .alert .message').html(errors_list_to_display);

                                        $('#modal-compagnie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification des taux
    $(document).on('click', '.btn_taux_compagnie', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-taux_compagnie').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-taux_compagnie').find('.modal-title').text(modal_title);
            $('#modal-taux_compagnie').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-taux_compagnie').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-taux_compagnie').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_taux_compagnie").on('click', function () {

                let formulaire = $('#form_taux_compagnie');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier ce ou ces taux ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-taux_compagnie .alert .message').html(errors_list_to_display);

                                                $('#modal-taux_compagnie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Modification d'un compagnie
    $(document).on('click', '.btn_modifier_compagnie', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_compagnie').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_compagnie').find('.modal-title').text(modal_title);
            $('#modal-modification_compagnie').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_compagnie').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-modification_compagnie').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_compagnie").on('click', function () {

                let formulaire = $('#form_update_compagnie');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cet compagnie ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_compagnie .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_compagnie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un compagnie
    $(document).on('click', '.btn_supprimer_compagnie', function () {
        let compagnie_id = $(this).data('compagnie_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette compagnie ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { compagnie_id: compagnie_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une businessunit
    $(document).on('click', "#btn_save_businessunit", function () {

        let formulaire = $('#form_add_businessunit');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer cette businessunit ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-businessunit .alert .message').html(errors_list_to_display);

                                        $('#modal-businessunit .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un businessunit
    $(document).on('click', '.btn_modifier_businessunit', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_businessunit').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_businessunit').find('.modal-title').text(modal_title);
            $('#modal-modification_businessunit').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_businessunit').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_businessunit').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_businessunit").on('click', function () {

                let formulaire = $('#form_update_businessunit');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cet businessunit ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_businessunit .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_businessunit .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un businessunit
    $(document).on('click', '.btn_supprimer_businessunit', function () {
        let businessunit_id = $(this).data('businessunit_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette businessunit ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { businessunit_id: businessunit_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une carosserie
    $(document).on('click', "#btn_save_carosserie", function () {

        let formulaire = $('#form_add_carosserie');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer cette carosserie ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-carosserie .alert .message').html(errors_list_to_display);

                                        $('#modal-carosserie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une carosserie
    $(document).on('click', '.btn_modifier_carosserie', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_carosserie').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_carosserie').find('.modal-title').text(modal_title);
            $('#modal-modification_carosserie').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_carosserie').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_carosserie').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_carosserie").on('click', function () {

                let formulaire = $('#form_update_carosserie');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cette carosserie ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_carosserie .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_carosserie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une carosserie
    $(document).on('click', '.btn_supprimer_carosserie', function () {
        let carosserie_id = $(this).data('carosserie_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette carosserie ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { carosserie_id: carosserie_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une catégorie véhicule
    $(document).on('click', "#btn_save_categorievehicule", function () {

        let formulaire = $('#form_add_categorievehicule');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer cette catégorie véhicule ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-categorievehicule .alert .message').html(errors_list_to_display);

                                        $('#modal-categorievehicule .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une catégorie véhicule
    $(document).on('click', '.btn_modifier_categorievehicule', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_categorievehicule').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_categorievehicule').find('.modal-title').text(modal_title);
            $('#modal-modification_categorievehicule').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_categorievehicule').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_categorievehicule').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_categorievehicule").on('click', function () {

                let formulaire = $('#form_update_categorievehicule');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cette catégorie véhicule ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_categorievehicule .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_categorievehicule .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une catégorie véhicule
    $(document).on('click', '.btn_supprimer_categorievehicule', function () {
        let categorievehicule_id = $(this).data('categorievehicule_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette catégorie véhicule ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { categorievehicule_id: categorievehicule_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une civilité
    $(document).on('click', "#btn_save_civilite", function () {

        let formulaire = $('#form_add_civilite');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer cette civilité ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-civilite .alert .message').html(errors_list_to_display);

                                        $('#modal-civilite .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une civilité
    $(document).on('click', '.btn_modifier_civilite', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_civilite').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_civilite').find('.modal-title').text(modal_title);
            $('#modal-modification_civilite').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_civilite').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_civilite').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_civilite").on('click', function () {

                let formulaire = $('#form_update_civilite');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier cette civilité ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_civilite .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_civilite .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une civilité
    $(document).on('click', '.btn_supprimer_civilite', function () {
        let civilite_id = $(this).data('civilite_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer cette civilité ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { civilite_id: civilite_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un compte trésorerie
    $(document).on('click', "#btn_save_comptetresorerie", function () {

        let formulaire = $('#form_add_comptetresorerie');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer ce compte trésorerie ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-comptetresorerie .alert .message').html(errors_list_to_display);

                                        $('#modal-comptetresorerie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un compte trésorerie
    $(document).on('click', '.btn_modifier_comptetresorerie', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_comptetresorerie').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_comptetresorerie').find('.modal-title').text(modal_title);
            $('#modal-modification_comptetresorerie').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_comptetresorerie').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_comptetresorerie').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_comptetresorerie").on('click', function () {

                let formulaire = $('#form_update_comptetresorerie');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: 'Voulez-vous vraiment modifier ce compte trésorerie ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_comptetresorerie .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_comptetresorerie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un compte trésorerie
    $(document).on('click', '.btn_supprimer_comptetresorerie', function () {
        let comptetresorerie_id = $(this).data('comptetresorerie_id');
        let href = $(this).data('href');
        let n = noty({
            text: 'Voulez-vous vraiment supprimer ce compte trésorerie ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { comptetresorerie_id: comptetresorerie_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une condition d'assurance
    $(document).on('click', "#btn_save_conditionsassurance", function () {

        let formulaire = $('#form_add_conditionsassurance');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer cette condition d'assurance ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-conditionsassurance .alert .message').html(errors_list_to_display);

                                        $('#modal-conditionsassurance .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une condition d'assurance
    $(document).on('click', '.btn_modifier_conditionsassurance', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_conditionsassurance').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_conditionsassurance').find('.modal-title').text(modal_title);
            $('#modal-modification_conditionsassurance').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_conditionsassurance').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_conditionsassurance').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_conditionsassurance").on('click', function () {

                let formulaire = $('#form_update_conditionsassurance');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier cette condition d'assurance ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_conditionsassurance .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_conditionsassurance .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une condition d'assurance
    $(document).on('click', '.btn_supprimer_conditionsassurance', function () {
        let conditionsassurance_id = $(this).data('conditionsassurance_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer cette condition d'assurance ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { conditionsassurance_id: conditionsassurance_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une dévise
    $(document).on('click', "#btn_save_devise", function () {

        let formulaire = $('#form_add_devise');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer cette dévise ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-devise .alert .message').html(errors_list_to_display);

                                        $('#modal-devise .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une dévise
    $(document).on('click', '.btn_modifier_devise', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_devise').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_devise').find('.modal-title').text(modal_title);
            $('#modal-modification_devise').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_devise').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_devise').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_devise").on('click', function () {

                let formulaire = $('#form_update_devise');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier cette dévise ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_devise .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_devise .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une dévise
    $(document).on('click', '.btn_supprimer_devise', function () {
        let devise_id = $(this).data('devise_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer cette dévise ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { devise_id: devise_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une énergie
    $(document).on('click', "#btn_save_carburant", function () {

        let formulaire = $('#form_add_carburant');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer cette énergie ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-carburant .alert .message').html(errors_list_to_display);

                                        $('#modal-carburant .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une énergie
    $(document).on('click', '.btn_modifier_carburant', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_carburant').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_carburant').find('.modal-title').text(modal_title);
            $('#modal-modification_carburant').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_carburant').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_carburant').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_carburant").on('click', function () {

                let formulaire = $('#form_update_carburant');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier cette énergie ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_carburant .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_carburant .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une énergie
    $(document).on('click', '.btn_supprimer_carburant', function () {
        let carburant_id = $(this).data('carburant_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer cette énergie ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { carburant_id: carburant_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une formule
    $(document).on('click', "#btn_save_formule", function () {

        let formulaire = $('#form_add_formule');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer cette formule ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-formule .alert .message').html(errors_list_to_display);

                                        $('#modal-formule .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une formule
    $(document).on('click', '.btn_modifier_formule', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_formule').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_formule').find('.modal-title').text(modal_title);
            $('#modal-modification_formule').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_formule').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_formule').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_formule").on('click', function () {

                let formulaire = $('#form_update_formule');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier cette formule ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_formule .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_formule .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une formule
    $(document).on('click', '.btn_supprimer_formule', function () {
        let formule_id = $(this).data('formule_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer cette formule ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { formule_id: formule_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un fractionnement
    $(document).on('click', "#btn_save_fractionnement", function () {

        let formulaire = $('#form_add_fractionnement');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce fractionnement ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-fractionnement .alert .message').html(errors_list_to_display);

                                        $('#modal-fractionnement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un fractionnement
    $(document).on('click', '.btn_modifier_fractionnement', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_fractionnement').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_fractionnement').find('.modal-title').text(modal_title);
            $('#modal-modification_fractionnement').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_fractionnement').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_fractionnement').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_fractionnement").on('click', function () {

                let formulaire = $('#form_update_fractionnement');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce fractionnement ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_fractionnement .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_fractionnement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un fractionnement
    $(document).on('click', '.btn_supprimer_fractionnement', function () {
        let fractionnement_id = $(this).data('fractionnement_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce fractionnement ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { fractionnement_id: fractionnement_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une garantie
    $(document).on('click', "#btn_save_garantie", function () {

        let formulaire = $('#form_add_garantie');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer cette garantie ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-garantie .alert .message').html(errors_list_to_display);

                                        $('#modal-garantie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une garantie
    $(document).on('click', '.btn_modifier_garantie', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_garantie').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_garantie').find('.modal-title').text(modal_title);
            $('#modal-modification_garantie').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_garantie').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_garantie').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_garantie").on('click', function () {

                let formulaire = $('#form_update_garantie');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier cette garantie ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_garantie .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_garantie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une garantie
    $(document).on('click', '.btn_supprimer_garantie', function () {
        let garantie_id = $(this).data('garantie_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer cette garantie ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { garantie_id: garantie_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une garantie / formule
    $(document).on('click', "#btn_save_garantieformule", function () {

        let formulaire = $('#form_add_garantieformule');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer cette garantie / formule ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-garantieformule .alert .message').html(errors_list_to_display);

                                        $('#modal-garantieformule .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une garantie / formule
    $(document).on('click', '.btn_modifier_garantieformule', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_garantieformule').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_garantieformule').find('.modal-title').text(modal_title);
            $('#modal-modification_garantieformule').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_garantieformule').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_garantieformule').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_garantieformule").on('click', function () {

                let formulaire = $('#form_update_garantieformule');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier cette garantie / formule ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_garantieformule .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_garantieformule .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une garantie / formule
    $(document).on('click', '.btn_supprimer_garantieformule', function () {
        let garantieformule_id = $(this).data('garantieformule_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer cette garantie / formule ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { garantieformule_id: garantieformule_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une garantie / circonstance
    $(document).on('click', "#btn_save_garantiecirconstance", function () {

        let formulaire = $('#form_add_garantiecirconstance');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer cette garantie / circonstance ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-garantiecirconstance .alert .message').html(errors_list_to_display);

                                        $('#modal-garantiecirconstance .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une garantie / circonstance
    $(document).on('click', '.btn_modifier_garantiecirconstance', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_garantiecirconstance').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_garantiecirconstance').find('.modal-title').text(modal_title);
            $('#modal-modification_garantiecirconstance').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_garantiecirconstance').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_garantiecirconstance').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_garantiecirconstance").on('click', function () {

                let formulaire = $('#form_update_garantiecirconstance');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier cette garantie / circonstance ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_garantiecirconstance .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_garantiecirconstance .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une garantie / circonstance
    $(document).on('click', '.btn_supprimer_garantiecirconstance', function () {
        let garantiecirconstance_id = $(this).data('garantiecirconstance_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer cette garantie / circonstance ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { garantiecirconstance_id: garantiecirconstance_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un groupe
    $(document).on('click', "#btn_save_groupe", function () {

        let formulaire = $('#form_add_groupe');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce groupe ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-groupe .alert .message').html(errors_list_to_display);

                                        $('#modal-groupe .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un groupe
    $(document).on('click', '.btn_modifier_groupe', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_groupe').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_groupe').find('.modal-title').text(modal_title);
            $('#modal-modification_groupe').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_groupe').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_groupe').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_groupe").on('click', function () {

                let formulaire = $('#form_update_groupe');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce groupe ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_groupe .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_groupe .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un groupe
    $(document).on('click', '.btn_supprimer_groupe', function () {
        let groupe_id = $(this).data('groupe_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce groupe ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { groupe_id: groupe_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un mode de règlement
    $(document).on('click', "#btn_save_modereglement", function () {

        let formulaire = $('#form_add_modereglement');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce mode de règlement ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-modereglement .alert .message').html(errors_list_to_display);

                                        $('#modal-modereglement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un mode de règlement
    $(document).on('click', '.btn_modifier_modereglement', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_modereglement').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_modereglement').find('.modal-title').text(modal_title);
            $('#modal-modification_modereglement').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_modereglement').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_modereglement').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_modereglement").on('click', function () {

                let formulaire = $('#form_update_modereglement');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce mode de règlement ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_modereglement .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_modereglement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un mode de règlement
    $(document).on('click', '.btn_supprimer_modereglement', function () {
        let modereglement_id = $(this).data('modereglement_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce mode de règlement ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { modereglement_id: modereglement_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un secteur d'activité
    $(document).on('click', "#btn_save_secteuractivite", function () {

        let formulaire = $('#form_add_secteuractivite');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce secteur d'activité ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-secteuractivite .alert .message').html(errors_list_to_display);

                                        $('#modal-secteuractivite .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un secteur d'activité
    $(document).on('click', '.btn_modifier_secteuractivite', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_secteuractivite').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_secteuractivite').find('.modal-title').text(modal_title);
            $('#modal-modification_secteuractivite').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_secteuractivite').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_secteuractivite').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_secteuractivite").on('click', function () {

                let formulaire = $('#form_update_secteuractivite');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce secteur d'activité ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_secteuractivite .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_secteuractivite .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un secteur d'activité
    $(document).on('click', '.btn_supprimer_secteuractivite', function () {
        let secteuractivite_id = $(this).data('secteuractivite_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce secteur d'activité ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { secteuractivite_id: secteuractivite_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un pays
    $(document).on('click', "#btn_save_pays", function () {

        let formulaire = $('#form_add_pays');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce pays ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-pays .alert .message').html(errors_list_to_display);

                                        $('#modal-pays .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un pays
    $(document).on('click', '.btn_modifier_pays', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_pays').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_pays').find('.modal-title').text(modal_title);
            $('#modal-modification_pays').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_pays').find('.modal-dialog').addClass('modal-xl').removeClass('modal-lg');

            //
            $('#modal-modification_pays').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_pays").on('click', function () {

                let formulaire = $('#form_update_pays');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce pays ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_pays .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_pays .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un pays
    $(document).on('click', '.btn_supprimer_pays', function () {
        let pays_id = $(this).data('pays_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce pays ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { pays_id: pays_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un type de document
    $(document).on('click', "#btn_save_type_document", function () {

        let formulaire = $('#form_add_type_document');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce type de document ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-type_document .alert .message').html(errors_list_to_display);

                                        $('#modal-type_document .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un type de document
    $(document).on('click', '.btn_modifier_typedocument', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_type_document').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_type_document').find('.modal-title').text(modal_title);
            $('#modal-modification_type_document').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_type_document').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_type_document').modal();

            //gestion du clique sur valider les modifications
            $("#btn_save_modification_type_document").on('click', function () {

                let formulaire = $('#form_update_modification_type_document');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce type de document ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_type_document .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_type_document .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un type de document
    $(document).on('click', '.btn_supprimer_typedocument', function () {
        let type_document_id = $(this).data('type_document_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce type de document ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { type_document_id: type_document_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une circonstance
    $(document).on('click', "#btn_save_circonstance", function () {

        let formulaire = $('#form_add_circonstance');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer cette circonstance ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-circonstance .alert .message').html(errors_list_to_display);

                                        $('#modal-circonstance .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une circonstance
    $(document).on('click', '.btn_modifier_circonstance', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_circonstance').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_circonstance').find('.modal-title').text(modal_title);
            $('#modal-modification_circonstance').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_circonstance').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_circonstance').modal();

            //gestion du clique sur valider les modifications
            $("#btn_update_circonstance").on('click', function () {

                let formulaire = $('#form_update_circonstance');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier cette circonstance ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_circonstance .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_circonstance .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une circonstance
    $(document).on('click', '.btn_supprimer_circonstance', function () {
        let circonstance_id = $(this).data('circonstance_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer cette circonstance ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { circonstance_id: circonstance_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'une responsabilité
    $(document).on('click', "#btn_save_responsabilite", function () {

        let formulaire = $('#form_add_responsabilite');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer cette responsabilité ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-responsabilite .alert .message').html(errors_list_to_display);

                                        $('#modal-responsabilite .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'une responsabilité
    $(document).on('click', '.btn_modifier_responsabilite', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_responsabilite').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_responsabilite').find('.modal-title').text(modal_title);
            $('#modal-modification_responsabilite').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_responsabilite').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_responsabilite').modal();

            //gestion du clique sur valider les modifications
            $("#btn_update_responsabilite").on('click', function () {

                let formulaire = $('#form_update_responsabilite');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier cette responsabilité ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_responsabilite .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_responsabilite .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'une responsabilité
    $(document).on('click', '.btn_supprimer_responsabilite', function () {
        let responsabilite_id = $(this).data('responsabilite_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer cette responsabilité ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { responsabilite_id: responsabilite_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un type d'intervenant
    $(document).on('click', "#btn_save_typeintervenant", function () {

        let formulaire = $('#form_add_typeintervenant');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce type d'intervenant ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-typeintervenant .alert .message').html(errors_list_to_display);

                                        $('#modal-typeintervenant .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un type d'intervenant
    $(document).on('click', '.btn_modifier_typeintervenant', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_typeintervenant').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_typeintervenant').find('.modal-title').text(modal_title);
            $('#modal-modification_typeintervenant').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_typeintervenant').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_typeintervenant').modal();

            //gestion du clique sur valider les modifications
            $("#btn_update_typeintervenant").on('click', function () {

                let formulaire = $('#form_update_typeintervenant');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce type d'intervenant ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_typeintervenant .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_typeintervenant .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un type d'intervenant
    $(document).on('click', '.btn_supprimer_typeintervenant', function () {
        let type_intervenant_id = $(this).data('type_intervenant_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce type d'intervenant ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { type_intervenant_id: type_intervenant_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un type de mouvement
    $(document).on('click', "#btn_save_typemouvement", function () {

        let formulaire = $('#form_add_typemouvement');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce type de mouvement ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-typemouvement .alert .message').html(errors_list_to_display);

                                        $('#modal-typemouvement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un type de mouvement
    $(document).on('click', '.btn_modifier_typemouvement', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_typemouvement').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_typemouvement').find('.modal-title').text(modal_title);
            $('#modal-modification_typemouvement').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_typemouvement').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_typemouvement').modal();

            //gestion du clique sur valider les modifications
            $("#btn_update_typemouvement").on('click', function () {

                let formulaire = $('#form_update_typemouvement');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce type de mouvement ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_typemouvement .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_typemouvement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un type de mouvement
    $(document).on('click', '.btn_supprimer_typemouvement', function () {
        let type_mouvement_id = $(this).data('type_mouvement_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce type de mouvement ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { type_mouvement_id: type_mouvement_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un type de sinistre
    $(document).on('click', "#btn_save_typesinistre", function () {

        let formulaire = $('#form_add_typesinistre');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce type de sinistre ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-typesinistre .alert .message').html(errors_list_to_display);

                                        $('#modal-typesinistre .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un type de sinistre
    $(document).on('click', '.btn_modifier_typesinistre', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_typesinistre').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_typesinistre').find('.modal-title').text(modal_title);
            $('#modal-modification_typesinistre').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_typesinistre').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_typesinistre').modal();

            //gestion du clique sur valider les modifications
            $("#btn_update_typesinistre").on('click', function () {

                let formulaire = $('#form_update_typesinistre');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce type de sinistre ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_typesinistre .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_typesinistre .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un type de sinistre
    $(document).on('click', '.btn_supprimer_typesinistre', function () {
        let type_sinistre_id = $(this).data('type_sinistre_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce type de sinistre ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { type_sinistre_id: type_sinistre_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un mouvement
    $(document).on('click', "#btn_save_mouvement", function () {

        let formulaire = $('#form_add_mouvement');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce mouvement ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-mouvement .alert .message').html(errors_list_to_display);

                                        $('#modal-mouvement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un mouvement
    $(document).on('click', '.btn_modifier_mouvement', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_mouvement').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_mouvement').find('.modal-title').text(modal_title);
            $('#modal-modification_mouvement').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_mouvement').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_mouvement').modal();

            //gestion du clique sur valider les modifications
            $("#btn_update_mouvement").on('click', function () {

                let formulaire = $('#form_update_mouvement');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce mouvement ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_mouvement .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_mouvement .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un mouvement
    $(document).on('click', '.btn_supprimer_mouvement', function () {
        let mouvement_id = $(this).data('mouvement_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce mouvement ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { mouvement_id: mouvement_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création d'un motif
    $(document).on('click', "#btn_save_motif", function () {

        let formulaire = $('#form_add_motif');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce motif ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    } else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-motif .alert .message').html(errors_list_to_display);

                                        $('#modal-motif .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Import des datas
    $(document).on('click', "#btn_save_import_motif", function () {

        let formulaire = $('#form_add_motif_import');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();
        let files = $('#form_add_motif_import #fichier')[0].files;

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment enregistrer les datas importées ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu
                            if (files.length > 0) {
                                formData.append('fichier', files[0]);
                            }

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            formulaire[0].reset();
                                            location.reload();
                                        });

                                    } else {

                                        $('#modal-import_motif .alert .message').html(response.message);

                                        $('#modal-import_motif .alert').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(5000);
                                        }).removeClass('alert-success').addClass('alert-warning');
                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });
                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
        }

        else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Modification d'un motif
    $(document).on('click', '.btn_modifier_motif', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_motif').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_motif').find('.modal-title').text(modal_title);
            $('#modal-modification_motif').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_motif').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_motif').modal();

            //gestion du clique sur valider les modifications
            $("#btn_update_motif").on('click', function () {

                let formulaire = $('#form_update_motif');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce motif ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();

                                    //confirmation obtenu

                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {

                                            if (response.statut == 1) {

                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });

                                            } else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_motif .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_motif .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');

                                            }

                                        },
                                        error: function (request, status, error) {

                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }

                                    });

                                    //fin confirmation obtenue

                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    //confirmation refusée
                                    $noty.close();

                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });

                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }

            });

        });

    });

    //Suppression d'un motif
    $(document).on('click', '.btn_supprimer_motif', function () {
        let motif_id = $(this).data('motif_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce motif ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { motif_id: motif_id },
                            success: function (response) {

                                notifySuccess(response.message, function () {
                                    location.reload();
                                });

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //Création du poste de dommage
    $(document).on('click', "#btn_save_postedommage", function () {

        let formulaire = $('#form_add_postedommage');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: "Voulez-vous vraiment enregistrer ce poste de dommage ?",
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    }
                                    if (response.statut == 0) {
                                        notifyWarning(response.message, function () {
                                            //location.reload();
                                        });
                                    }
                                    else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-postedommage .alert .message').html(errors_list_to_display);

                                        $('#modal-postedommage .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }
                            });
                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();
                        }
                    }
                ]
            });

        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });
            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }
    });

    //Modification du poste de dommage
    $(document).on('click', '.btn_modifier_postedommage', function () {

        let model_name = $(this).attr('data-model_name');
        let modal_title = $(this).attr('data-modal_title');
        let href = $(this).attr('data-href');

        $('#olea_std_dialog_box').load(href, function () {

            //appliquer le mask de saisie sur les champs montant
            AppliquerMaskSaisie();

            $('#modal-modification_postedommage').attr('data-backdrop', 'static').attr('data-keyboard', false);

            $('#modal-modification_postedommage').find('.modal-title').text(modal_title);
            $('#modal-modification_postedommage').find('#btn_valider').attr({ 'data-model_name': model_name, 'data-href': href });
            $('#modal-modification_postedommage').find('.modal-dialog').addClass('modal-lg').removeClass('modal-xl');

            //
            $('#modal-modification_postedommage').modal();

            //gestion du clique sur valider les modifications
            $("#btn_update_postedommage").on('click', function () {

                let formulaire = $('#form_update_postedommage');
                let href = formulaire.attr('action');

                $.validator.setDefaults({ ignore: [] });

                let formData = new FormData();

                if (formulaire.valid()) {

                    //demander confirmation
                    let n = noty({
                        text: "Voulez-vous vraiment modifier ce poste de dommage ?",
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                                    $noty.close();
                                    let data_serialized = formulaire.serialize();
                                    $.each(data_serialized.split('&'), function (index, elem) {
                                        let vals = elem.split('=');

                                        let key = vals[0];
                                        let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                        formData.append(key, valeur);

                                    });

                                    $.ajax({
                                        type: 'post',
                                        url: href,
                                        data: formData,
                                        processData: false,
                                        contentType: false,
                                        success: function (response) {
                                            if (response.statut == 1) {
                                                notifySuccess(response.message, function () {
                                                    location.reload();
                                                });
                                            }
                                            if (response.statut == 0) {
                                                notifyWarning(response.message, function () {
                                                    //location.reload();
                                                });
                                            }
                                            else {

                                                let errors = JSON.parse(JSON.stringify(response.errors));
                                                let errors_list_to_display = '';
                                                for (field in errors) {
                                                    errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                                }

                                                $('#modal-modification_postedommage .alert .message').html(errors_list_to_display);

                                                $('#modal-modification_postedommage .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                                    $(this).slideUp(500);
                                                }).removeClass('alert-success').addClass('alert-warning');
                                            }
                                        },
                                        error: function (request, status, error) {
                                            notifyWarning("Erreur lors de l'enregistrement");
                                        }
                                    });
                                }
                            },
                            {
                                addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                                    $noty.close();
                                }
                            }
                        ]
                    });

                } else {

                    $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                    let validator = formulaire.validate();

                    $.each(validator.errorMap, function (index, value) {

                        console.log('Id: ' + index + ' Message: ' + value);

                    });
                    notifyWarning('Veuillez renseigner tous les champs obligatoires');
                }
            });
        });
    });

    //Suppression du poste de dommage
    $(document).on('click', '.btn_supprimer_postedommage', function () {
        let postedommage_id = $(this).data('postedommage_id');
        let href = $(this).data('href');
        let n = noty({
            text: "Voulez-vous vraiment supprimer ce poste de dommage ?",
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: href,
                            type: 'post',
                            data: { postedommage_id: postedommage_id },
                            success: function (response) {
                                if (response.statut == 1) {
                                    notifySuccess(response.message, function () {
                                        location.reload();
                                    });
                                } else {
                                    notifyWarning(response.message, function () {
                                        //location.reload();
                                    });
                                }
                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });
    });

    //TODO ANALYSE & CONTRÔLE
    //Création d'un portefeuille par compagnie
    $(document).on('click', "#btn_save_portefeuille_compagnie", function () {

        let formulaire = $('#form_add_portefeuille_compagnie');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment importer le portefeuille ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        let fileContent = response.data.file_base64;
                                        let filename = response.data.filename;

                                        // Créer un lien de téléchargement
                                        let link = document.createElement("a");
                                        link.href = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," + fileContent;
                                        link.download = filename;

                                        // Ajouter le lien temporairement au DOM et le cliquer automatiquement
                                        document.body.appendChild(link);
                                        link.click();
                                        document.body.removeChild(link);

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    }
                                    if (response.statut == 0){
                                        notifyWarning(response.message);
                                    }
                                    else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-compagnie .alert .message').html(errors_list_to_display);

                                        $('#modal-compagnie .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Création d'un portefeuille par commercial
    $(document).on('click', "#btn_save_portefeuille_commercial", function () {

        let formulaire = $('#form_add_portefeuille_commercial');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment importer le portefeuille ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        let fileContent = response.data.file_base64;
                                        let filename = response.data.filename;

                                        // Créer un lien de téléchargement
                                        let link = document.createElement("a");
                                        link.href = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," + fileContent;
                                        link.download = filename;

                                        // Ajouter le lien temporairement au DOM et le cliquer automatiquement
                                        document.body.appendChild(link);
                                        link.click();
                                        document.body.removeChild(link);

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    }
                                    if (response.statut == 0){
                                        notifyWarning(response.message);
                                    }
                                    else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-commercial .alert .message').html(errors_list_to_display);

                                        $('#modal-commercial .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

    //Création d'un portefeuille par business_unit
    $(document).on('click', "#btn_save_portefeuille_business_unit", function () {

        let formulaire = $('#form_add_portefeuille_business_unit');
        let href = formulaire.attr('action');

        $.validator.setDefaults({ ignore: [] });

        let formData = new FormData();

        if (formulaire.valid()) {

            //demander confirmation
            let n = noty({
                text: 'Voulez-vous vraiment importer le portefeuille ?',
                type: 'warning',
                dismissQueue: true,
                layout: 'center',
                theme: 'defaultTheme',
                buttons: [
                    {
                        addClass: 'btn btn-primary', text: 'OUI', onClick: function ($noty) {
                            $noty.close();

                            //confirmation obtenu

                            let data_serialized = formulaire.serialize();
                            $.each(data_serialized.split('&'), function (index, elem) {
                                let vals = elem.split('=');

                                let key = vals[0];
                                let valeur = decodeURIComponent(vals[1].replace(/\+/g, '  '));

                                formData.append(key, valeur);

                            });

                            $.ajax({
                                type: 'post',
                                url: href,
                                data: formData,
                                processData: false,
                                contentType: false,
                                success: function (response) {

                                    if (response.statut == 1) {

                                        let fileContent = response.data.file_base64;
                                        let filename = response.data.filename;

                                        // Créer un lien de téléchargement
                                        let link = document.createElement("a");
                                        link.href = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," + fileContent;
                                        link.download = filename;

                                        // Ajouter le lien temporairement au DOM et le cliquer automatiquement
                                        document.body.appendChild(link);
                                        link.click();
                                        document.body.removeChild(link);

                                        notifySuccess(response.message, function () {
                                            location.reload();
                                        });

                                    }
                                    if (response.statut == 0){
                                        notifyWarning(response.message);
                                    }
                                    else {

                                        let errors = JSON.parse(JSON.stringify(response.errors));
                                        let errors_list_to_display = '';
                                        for (field in errors) {
                                            errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                                        }

                                        $('#modal-business_unit .alert .message').html(errors_list_to_display);

                                        $('#modal-business_unit .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                            $(this).slideUp(500);
                                        }).removeClass('alert-success').addClass('alert-warning');

                                    }

                                },
                                error: function (request, status, error) {

                                    notifyWarning("Erreur lors de l'enregistrement");
                                }

                            });

                            //fin confirmation obtenue

                        }
                    },
                    {
                        addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                            //confirmation refusée
                            $noty.close();

                        }
                    }
                ]
            });
            //fin demande confirmation


        } else {

            $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

            let validator = formulaire.validate();

            $.each(validator.errorMap, function (index, value) {

                console.log('Id: ' + index + ' Message: ' + value);

            });

            notifyWarning('Veuillez renseigner correctement le forumulaire');
        }

    });

     //TODO GARANTIE / FORMULE
    // Insertion d'une ligne supplémentaire dans l'onglet GARANTIES/FORMULE - lors de l'ajout
    $(document).on("click", "#table_garanties #btnAddLigneGarantie", function () {
        // Vérifier que toutes les lignes existantes ont une garantie sélectionnée
        let allValid = true;
        $('#table_garanties tbody tr').each(function () {
            let selectField = $(this).find('.garantieformule');

            if (!selectField.val()) {
                allValid = false;
                selectField[0].reportValidity();
            }
        });

        if (!allValid) {
            return;
        }

        let tr = $('#table_garanties tbody tr:first');
        let timestamp = Date.now();

        // Ajouter une nouvelle ligne
        $('#table_garanties tbody tr:last')
            .after('<tr id="tr_' + timestamp + '">' + tr.html() + '</tr>')
            .ready(function () {
                let newTr = $('#tr_' + timestamp);

                // Réinitialiser les champs de la nouvelle ligne
                newTr.find('.garantieformule').val('');

                // Mettre à jour les options de chaque ligne
                updateOptions();
            });
    });

    // Supprimer une ligne
    $(document).on("click", ".btnSupprimerLigneGarantie", function () {
        let nombre_ligne = $('#table_garanties tbody tr').length;

        if (nombre_ligne > 1) {
            $(this).parent().parent().remove();
        } else {
            let tr_ligne_id = $('#table_garanties tbody tr').attr('id');
            resetFields('#' + tr_ligne_id);
        }

        updateOptions();
    });

    // Fonction pour réinitialiser les champs (si nécessaire)
    function resetFields(selector) {
        $(selector).find('.garantieformule').val('');

    }

    // Fonction pour mettre à jour les options des menus déroulants
    function updateOptions() {
        let selectedGaranties = [];
        $('#table_garanties tbody tr').each(function () {
            let selectedValue = $(this).find('.garantieformule').val();
            if (selectedValue) {
                selectedGaranties.push(selectedValue);
            }
        });

        // Mettre à jour les menus déroulants
        $('#table_garanties tbody tr').each(function () {
            let currentSelect = $(this).find('.garantieformule');
            let currentValue = currentSelect.val();

            currentSelect.find('option').each(function () {
                let optionValue = $(this).val();
                if (selectedGaranties.includes(optionValue) && optionValue !== currentValue) {
                    $(this).hide();
                } else {
                    $(this).show();
                }
            });
        });
    }

    // Insertion ligne supplémentaire dans l'onglet GARANTIES/FORMULES - lors de la modification
    $(document).on("click", "#table_garanties_modification #btnAddLigneGarantie_modification", function () {
        let allValid = true;
        $('#table_garanties_modification tbody tr').each(function () {
            let selectField = $(this).find('.garantieformule_modification');

            // Validation HTML5 "required"
            if (!selectField.val()) {
                allValid = false;
                selectField[0].reportValidity();
            }
        });

        if (!allValid) {
            // Si une ligne n'est pas valide, on arrête l'ajout
            return;
        }

        let trTemplate = $('#tr_initial_vide').html();
        let timestamp = Date.now();

        // Ajouter une nouvelle ligne
        $('#table_garanties_modification tbody tr:last')
            .after('<tr id="tr_' + timestamp + '">' + trTemplate + '</tr>')
            .ready(function () {
                let newTr = $('#tr_' + timestamp);

                // Réinitialiser les champs de la nouvelle ligne
                newTr.find('.garantieformule_modification').val('');

                updateOptionsModification();
            });
    });

    // Supprimer une ligne
    $(document).on("click", "#table_garanties_modification .btnSupprimerLigneGarantie_modification", function () {
        let nombre_ligne = $('#table_garanties_modification tbody tr').length;

        if (nombre_ligne > 1) {
            // Supprimer la ligne sélectionnée
            $(this).parent().parent().remove();

            updateOptionsModification();
        } else {
            alert("Vous ne pouvez pas supprimer toutes les lignes de garanties. Au moins une ligne doit être conservée.");
        }
    });

    // Fonction pour mettre à jour les options des menus déroulants
    function updateOptionsModification() {
        // Récupérer toutes les garanties déjà sélectionnées
        let selectedGaranties = [];
        $('#table_garanties_modification tbody tr').each(function () {
            let selectedValue = $(this).find('.garantieformule_modification').val();
            if (selectedValue) {
                selectedGaranties.push(selectedValue);
            }
        });

        // Mettre à jour les menus déroulants
        $('#table_garanties_modification tbody tr').each(function () {
            let currentSelect = $(this).find('.garantieformule_modification');
            let currentValue = currentSelect.val();

            // Conserver uniquement les options non sélectionnées ou la valeur actuelle
            currentSelect.find('option').each(function () {
                let optionValue = $(this).val();
                if (selectedGaranties.includes(optionValue) && optionValue !== currentValue) {
                    $(this).hide();
                } else {
                    $(this).show();
                }
            });
        });
    }

    // Insertion d'une ligne supplémentaire dans l'onglet GARANTIES/GARANTIES - lors de l'ajout
    $(document).on("click", "#table_garanties #btnAddLigneGarantieCirconstance", function () {
        // Vérifier que toutes les lignes existantes ont une garantie sélectionnée
        let allValid = true;
        $('#table_garanties tbody tr').each(function () {
            let selectField = $(this).find('.garantiecirconstance');

            if (!selectField.val()) {
                allValid = false;
                selectField[0].reportValidity();
            }
        });

        if (!allValid) {
            return;
        }

        let tr = $('#table_garanties tbody tr:first');
        let timestamp = Date.now();

        // Ajouter une nouvelle ligne
        $('#table_garanties tbody tr:last')
            .after('<tr id="tr_' + timestamp + '">' + tr.html() + '</tr>')
            .ready(function () {
                let newTr = $('#tr_' + timestamp);

                // Réinitialiser les champs de la nouvelle ligne
                newTr.find('.garantiecirconstance').val('');

                // Mettre à jour les options de chaque ligne
                updateOptions();
            });
    });

    // Supprimer une ligne
    $(document).on("click", ".btnSupprimerLigneGarantieCirconstance", function () {
        let nombre_ligne = $('#table_garanties tbody tr').length;

        if (nombre_ligne > 1) {
            $(this).parent().parent().remove();
        } else {
            let tr_ligne_id = $('#table_garanties tbody tr').attr('id');
            resetFields('#' + tr_ligne_id);
        }

        updateOptions();
    });

    // Fonction pour réinitialiser les champs (si nécessaire)
    function resetFields(selector) {
        $(selector).find('.garantiecirconstance').val('');

    }

    // Fonction pour mettre à jour les options des menus déroulants
    function updateOptions() {
        let selectedGaranties = [];
        $('#table_garanties tbody tr').each(function () {
            let selectedValue = $(this).find('.garantiecirconstance').val();
            if (selectedValue) {
                selectedGaranties.push(selectedValue);
            }
        });

        // Mettre à jour les menus déroulants
        $('#table_garanties tbody tr').each(function () {
            let currentSelect = $(this).find('.garantiecirconstance');
            let currentValue = currentSelect.val();

            currentSelect.find('option').each(function () {
                let optionValue = $(this).val();
                if (selectedGaranties.includes(optionValue) && optionValue !== currentValue) {
                    $(this).hide();
                } else {
                    $(this).show();
                }
            });
        });
    }

    // Insertion ligne supplémentaire dans l'onglet GARANTIES/CIRCONSTANCES - lors de la modification
    $(document).on("click", "#table_garanties_modification #btnAddLigneGarantieCirconstance_modification", function () {
        let allValid = true;
        $('#table_garanties_modification tbody tr').each(function () {
            let selectField = $(this).find('.garantiecirconstance_modification');

            // Validation HTML5 "required"
            if (!selectField.val()) {
                allValid = false;
                selectField[0].reportValidity();
            }
        });

        if (!allValid) {
            // Si une ligne n'est pas valide, on arrête l'ajout
            return;
        }

        let trTemplate = $('#tr_initial_vide').html();
        let timestamp = Date.now();

        // Ajouter une nouvelle ligne
        $('#table_garanties_modification tbody tr:last')
            .after('<tr id="tr_' + timestamp + '">' + trTemplate + '</tr>')
            .ready(function () {
                let newTr = $('#tr_' + timestamp);

                // Réinitialiser les champs de la nouvelle ligne
                newTr.find('.garantiecirconstance_modification').val('');

                updateOptionsModification();
            });
    });

    // Supprimer une ligne
    $(document).on("click", "#table_garanties_modification .btnSupprimerLigneGarantieCirconstance_modification", function () {
        let nombre_ligne = $('#table_garanties_modification tbody tr').length;

        if (nombre_ligne > 1) {
            // Supprimer la ligne sélectionnée
            $(this).parent().parent().remove();

            updateOptionsModification();
        } else {
            alert("Vous ne pouvez pas supprimer toutes les lignes de garanties. Au moins une ligne doit être conservée.");
        }
    });

    // Fonction pour mettre à jour les options des menus déroulants
    function updateOptionsModification() {
        // Récupérer toutes les garanties déjà sélectionnées
        let selectedGaranties = [];
        $('#table_garanties_modification tbody tr').each(function () {
            let selectedValue = $(this).find('.garantiecirconstance_modification').val();
            if (selectedValue) {
                selectedGaranties.push(selectedValue);
            }
        });

        // Mettre à jour les menus déroulants
        $('#table_garanties_modification tbody tr').each(function () {
            let currentSelect = $(this).find('.garantiecirconstance_modification');
            let currentValue = currentSelect.val();

            // Conserver uniquement les options non sélectionnées ou la valeur actuelle
            currentSelect.find('option').each(function () {
                let optionValue = $(this).val();
                if (selectedGaranties.includes(optionValue) && optionValue !== currentValue) {
                    $(this).hide();
                } else {
                    $(this).show();
                }
            });
        });
    }

    //TODO SIAKA
    //Création de courrier
    $("#btn_save_courrier").on('click', function () {
        let btn_save_courrier = $(this);
        let formulaire = $('#form_add_courrier');


        $.validator.setDefaults({ ignore: [] });

        if (formulaire.valid()) {
            // Envoi des données via AJAX
            $.ajax({
                type: 'post',
                url: formulaire.attr('action'),
                data: formulaire.serialize(),
                    beforeSend: function () {
                    $('#loading_gif').show();
                    btn_save_courrier.hide();
                },
                success: function (response) {
                    $('#loading_gif').hide();
                    btn_save_courrier.show();

                    if (response.statut === 1) {
                        // Notification de succès et rechargement de la page
                        notifySuccess(response.message, function () {
                            location.reload();
                        });
                    } else {
                        notifyWarning(response.message);
                    }
                },
                error: function (response) {
                    $('#loading_gif').hide(); //
                    btn_save_courrier.show(); //

                    console.error("Erreur lors de l'envoi AJAX :", response); //
                    notifyError("Une erreur est survenue lors de l'enregistrement. Veuillez réessayer.");
                }
            });
        } else {
            //
            notifyWarning("Veuillez renseigner tous les champs obligatoires.");
        }
    });

    //ouverture du dialog
    $(document).on("click", ".btn-modal-modifier_courrier", function () {

            let href = $(this).attr('data-href');

            $('#olea_std_dialog_box').load(href, function () {

                AppliquerMaskSaisie();

                $('#modal-courrier-update').attr('data-backdrop', 'static').attr('data-keyboard', false);

                $('#modal-courrier-update').find('.modal-dialog').addClass('modal-m');

                $('#modal_courrier_update').modal();
            });

        });

    //Valider les modifications
    $(document).on("click", "#btn_update_courrier", function () {

            let formulaire = $(this).closest('form');
            let href = formulaire.attr('action');

            if (formulaire.valid()) {

                $.ajax({
                    type: 'post',
                    url: href,
                    data: formulaire.serialize(),
                    success: function (response) {

                        if (response.statut == 1) {

                            courrier = response.data;

                            //Vider le formulaire
                            resetFields('#' + formulaire.attr('id'));

                            notifySuccess(response.message, function () {
                                location.reload();
                            });

                        } else {

                            let errors = JSON.parse(JSON.stringify(response.errors));
                            let errors_list_to_display = '';
                            for (field in errors) {
                                errors_list_to_display += '- ' + ucfirst(field) + ' : ' + errors[field] + '<br/>';
                            }

                            $('#modal-courrier .alert .message').html(errors_list_to_display);

                            $('#modal-courrier .alert ').fadeTo(2000, 500).slideUp(500, function () {
                                $(this).slideUp(500);
                            }).removeClass('alert-success').addClass('alert-warning');

                        }

                    },
                    error: function (request, status, error) {

                        notifyWarning("Erreur lors de l'enregistrement");
                    }

                });

            } else {

                $('label.error').css({ display: 'none', height: '0px' }).removeClass('error').text('');

                let validator = formulaire.validate();

                $.each(validator.errorMap, function (index, value) {

                    console.log('Id: ' + index + ' Message: ' + value);

                });

                notifyWarning('Veuillez renseigner correctement le formulaire');
            }

        });

    //Suppression de courrier
    $(document).on('click', '.btn_supprimer_courrier', function () {
        let courrier_id = $(this).data('courrier_id');

        let n = noty({
            text: 'Voulez-vous vraiment supprimer ce courrier ?',
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'Supprimer', onClick: function ($noty) {
                        $noty.close();

                        //effectuer la suppression
                        $.ajax({
                            url: '/production/courrier/delete',
                            type: 'post',
                            data: { courrier_id: courrier_id },
                            success: function (e) {

                                location.reload();

                            },
                            error: function () {
                                notifyWarning('Erreur lors de la suppression');
                            }
                        });

                    }
                },
                {
                    addClass: 'btn btn-danger', text: 'Annuler', onClick: function ($noty) {
                        //annuler la suppression
                        $noty.close();
                    }
                }
            ]
        });

    });

});

//Affichage du tableau si réponse apporteur est oui.
document.addEventListener('DOMContentLoaded', function () {
    const yesRadio = document.getElementById('yes_apporteur');
    const noRadio = document.getElementById('no_apporteur');
    const tableDiv = document.getElementById('test');
    const tableInputs = tableDiv.querySelectorAll('input, select, textarea');
    const commissionField = document.getElementById('total_commission_intermediaire');

    // Initial hide or show based on the default checked radio button
    tableDiv.style.display = noRadio.checked ? 'none' : 'block';

    // Add event listeners for the radio buttons
    yesRadio.addEventListener('change', function () {
        if (this.checked) {
            tableDiv.style.display = 'block';
        }
    });

    noRadio.addEventListener('change', function () {
        if (this.checked) {
            tableDiv.style.display = 'none';

            // Clear all inputs inside the table
            tableInputs.forEach(input => {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = false;
                } else {
                    input.value = '';
                }
            });

            // Reset the total commission field
            if (commissionField) {
                commissionField.value = '0';
            }
        }
    });
});

//TODO FABRICE Partie 1
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

    // Pour le téléchargement du fichier modèle de création d'aliment
    $('#telecharger_modele').on('click', function () {
        // Récupérer le chemin du fichier depuis l'attribut "download-fichier"
        const filePath = $(this).attr('download-fichier');

        // Vérifier l'existence du fichier via une requête fetch
        fetch(filePath, { method: 'HEAD' })
            .then(response => {
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

    // Apporteur
    function on_change_apporteur(response, mode) {
        let modal_id = mode === 'modification' ? '#modal-modification_police' : '#modal-police';
        let box_id = mode === 'modification' ? '#test_modification' : '#test';
        let total_id = mode === 'modification' ? '#total_commission_intermediaire_modification' : '#total_commission_intermediaire';

        if (response === 'OUI') {
            if ($(`${modal_id} ${box_id}`).length) {
                $(`${modal_id} ${box_id}`).show();
                $(`${modal_id} ${box_id} input, ${modal_id} ${box_id} select, ${modal_id} ${box_id} textarea`).attr('required', true);
            } else {
                console.error(`Element ${box_id} not found in ${modal_id}`);
            }
        } else {
            if ($(`${modal_id} ${box_id}`).length) {
                $(`${modal_id} ${box_id}`).hide();
                $(`${modal_id} ${box_id} input, ${modal_id} ${box_id} select, ${modal_id} ${box_id} textarea`).val('').removeAttr('required');
                $(`${modal_id} ${total_id}`).val('0');
            } else {
                console.error(`Element ${box_id} not found in ${modal_id}`);
            }
        }
    }

    // Attachement des événements pour les boutons radio apporteur
    $(document).on("change", "#modal-police input[name='apporteur']", function () {
        let response = $(this).val();
        on_change_apporteur(response, 'creation');
    });

    $(document).on("change", "#modal-modification_police input[name='apporteur']", function () {
        let response = $(this).val();
        on_change_apporteur(response, 'modification');
    });

    // Initialisation pour le mode modification
    $(document).ready(function () {
        let apporteur_response_modification = $("#modal-modification_police input[name='apporteur']:checked").val();
        if (apporteur_response_modification) {
            on_change_apporteur(apporteur_response_modification, 'modification');
        }

        let apporteur_response_creation = $("#modal-police input[name='apporteur']:checked").val();
        if (apporteur_response_creation) {
            on_change_apporteur(apporteur_response_creation, 'creation');
        }
    });

    function on_change_garantie(response, mode) {
        let modal_id = mode === 'modification' ? '#modal-modification_police' : '#modal-police';
        let box_id = mode === 'modification' ? '#test_garantie_modification' : '#test_garantie';
        let formule_id = mode === 'modification' ? '#formule_block_modification' : '#formule_block';

        if (response === 'OUI') {
            if ($(`${modal_id} ${box_id}`).length && $(`${modal_id} ${formule_id}`).length) {
                $(`${modal_id} ${box_id}`).show();
                $(`${modal_id} ${formule_id}`).show();
                $(`${modal_id} ${box_id} input`).show();
            } else {
                console.error(`Elements ${box_id} or ${formule_id} not found in ${modal_id}`);
            }
        } else {
            if ($(`${modal_id} ${box_id}`).length && $(`${modal_id} ${formule_id}`).length) {
                $(`${modal_id} ${box_id}`).hide();
                $(`${modal_id} ${formule_id}`).hide();
                $(`${modal_id} ${box_id} input`).val('').removeAttr('required');
            } else {
                console.error(`Elements ${box_id} or ${formule_id} not found in ${modal_id}`);
            }
        }
    }

    // Attachement des événements pour les boutons radio garantie
    $(document).on("change", "#modal-police input[name='garantie']", function () {
        let response = $(this).val();
        on_change_garantie(response, 'creation');
    });

    $(document).on("change", "#modal-modification_police input[name='garantie']", function () {
        let response = $(this).val();
        on_change_garantie(response, 'modification');
    });

    // Initialisation pour le mode modification
    $(document).ready(function () {
        let garantie_response_modification = $("#modal-modification_police input[name='garantie']:checked").val();
        if (garantie_response_modification) {
            on_change_garantie(garantie_response_modification, 'modification');
        }

        let garantie_response_creation = $("#modal-police input[name='garantie']:checked").val();
        if (garantie_response_creation) {
            on_change_garantie(garantie_response_creation, 'creation');
        }
    });


    function chargementGarantiesFormuleTable(formuleId) {
        // Efface le contenu existant du tableau sauf l'entête
        $("#table_garantie_police tbody").empty();

        // Effacer tout message précédent
        $('#garantie-message-error').text('').hide();
        $('#garantie-message-warning').text('').hide();

        // Vérifie qu'un ID produit a été sélectionné
        if (!formuleId) {
            return;
        }

        // Appel AJAX pour récupérer les garanties liées au produit
        $.ajax({
            url: "/production/get_garanties_by_formule/",
            type: "GET",
            data: { formule_id: formuleId },
            success: function (data) {
                if (data && data.garanties) {
                    // Parcourt les garanties et les ajoute dans le tableau
                    data.garanties.forEach((garantie, index) => {
                        let row = `
                            <tr>
                                <td style="vertical-align:middle;">
                                    <input type="checkbox" class="form-control garantie-checkbox" name="garantie_${garantie.id}" value="${garantie.id}" style="width: 1rem; height: 1.25rem;">
                                </td>
                                <td style="vertical-align:middle;">${garantie.nom}</td>
                                <td style="vertical-align:middle;padding:5px;">
                                    <input type="text" class="form-control form-control-sm franchise-input" name="franchise_${garantie.id}" value="" onkeypress="isInputNumber(event)" oninput="formatMontant(this)" disabled>
                                </td>
                                <td style="vertical-align:middle;padding:5px;">
                                    <input type="text" class="form-control form-control-sm capital-input" name="capital_${garantie.id}" value="" onkeypress="isInputNumber(event)" oninput="formatMontant(this)" disabled>
                                </td>
                            </tr>
                        `;
                        $("#table_garantie_police tbody").append(row);
                    });
                } else {
                    $('#garantie-message-warning').text('Aucune garantie trouvée pour ce produit.').show();
                    setTimeout(() => $('#garantie-message-error').fadeOut(), 5000);
                }
            },
            error: function (xhr, status, error) {
                $('#message-error').text(response.error || 'Erreur lors de la récupération des garanties.').show();
                setTimeout(() => $('#garantie-message-error').fadeOut(), 5000);
            },
        });

    }

    // Événement sur le changement de la formule sélectionnée
    $("#formule").change(function () {
        let formuleId = $(this).find(":selected").data("formule_id");
        if (formuleId) {
            chargementGarantiesFormuleTable(formuleId);
        }
    });

    // Surveiller les changements des cases à cocher
    $(document).on('change', '.garantie-checkbox', function () {
        // Récupérer la ligne parente (tr) de la case cochée/décochée
        const parentRow = $(this).closest('tr');

        // Trouver les champs franchise et capital associés
        const franchiseInput = parentRow.find('.franchise-input');
        const capitalInput = parentRow.find('.capital-input');

        if ($(this).is(':checked')) {
            // Activer les champs si la case est cochée
            franchiseInput.prop('disabled', false);
            capitalInput.prop('disabled', false);
        } else {
            // Désactiver et vider les champs si la case est décochée
            franchiseInput.prop('disabled', true).val('');
            capitalInput.prop('disabled', true).val('');
        }
    });

    // Lorsque le modal est complètement fermé
    $('#modal-police').on('hidden.bs.modal', function () {
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

    $("#importation_aliment").on("click", function () {
        const inputFichier = $("#fichier_aliment");
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
                    $("#fichier_aliment").trigger("reset");
                    $("#message-success").text(response.message).show().delay(5000).fadeOut();
                    console.log(response.data);
                    // Mettre à jour le tableau avec les nouvelles données
                    const tbody = $("#table_liste_aliment tbody");
                    response.data.forEach((row, index) => {
                        tbody.append(`
                            <tr data-index="${index}">
                                <td>
                                    <button class="btn btn-danger btn-sm" onclick="supprimerAliment(${index})">
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

                    $('#fichier_aliment').removeClass('is-valid').removeClass('is-invalid');

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

    $('#btn_save_police_aliment').on('click', function () {
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
        const formData = new FormData($('#form_add_police_aliment')[0]);

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
                    const tbody = $("#table_liste_aliment tbody");
                    response.data.forEach((row, index) => {
                        tbody.append(`
                            <tr data-index="${index}">
                                <td>
                                    <button class="btn btn-danger btn-sm" onclick="supprimerAliment(${index})">
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
                    $("#form_add_police_aliment").trigger("reset");
                    $("#form_add_police_aliment select").each(function() {
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

    $(document).on('click', '.btn-danger', function () {
        const index = $(this).closest('tr').data('index');
        supprimerAliment(index);
    });

    // Fonction pour supprimer un aliment via AJAX en utilisant l'index
    function supprimerAliment(index) {
        $.ajax({
            url: `/production/supprimer_aliment/${index}/`,
            type: 'POST',
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            success: function (response) {
                if (response.success) {
                    // Si la suppression est réussie, supprime la ligne correspondante du tableau
                    $(`tr[data-index="${index}"]`).remove();
                } else {
                    console.error(response.error || 'Erreur lors de la suppression.');
                }
            },
            error: function () {
                console.error('Erreur de communication avec le serveur.');
            }
        });
    }

    //Changement de branche, charger les produits liés
    $('#branche').on('change', function () {

        let branche_id = $(this).val();
        $('#produit').html('<option value="">---------------------------</option>');

        $.ajax({
            type: 'get',
            url: '/production/branche/' + branche_id + '/produits',
            success: function (produits) {

                $('#produit').html('').append('<option value="">Sélectionnez un produit</option>');

                produits.forEach(function (produit) {
                    $('#produit').append('<option value="' + produit.pk + '" data-produit-code="' + produit.fields.code + '">' + produit.fields.libelle + '</option>');
                });

            },
            error: function () { }
        });
    });

    // Initialisation lors du chargement de la page
    $("#typecompagnie").val("");
    $(".box_typecompagnie").hide();
    $("#box_compagnie").hide();
    $("#compagnie_id").empty().append('<option value="">Choisir</option>');

    // Gestion du changement dans le champ "compagnie"
    $("#compagnie").on("change", function () {
        const selectedCompagnieId = $(this).val();

        if (selectedCompagnieId) {
            // Si une compagnie est choisie, afficher le champ "Autre assureur"
            $(".box_typecompagnie").show();
            $("#typecompagnie").val("");
            $("#box_compagnie").hide();
            $("#compagnie_id").empty().append('<option value="">Choisir</option>');
        } else {
            // Si aucune compagnie n'est choisie, cacher le champ "Autre assureur" et réinitialiser
            $(".box_typecompagnie").hide();
            $("#typecompagnie").val("");
            $("#box_compagnie").hide();
            $("#compagnie_id").empty().append('<option value="">Choisir</option>');
        }
    });

    // Gestion du changement dans le champ "typecompagnie"
    $("#typecompagnie").on("change", function () {
        const selectedTypeId = $(this).val();
        const selectedCompagnieId = $("#compagnie").val();

        if (selectedTypeId) {
            // Si un type de compagnie est sélectionné, afficher les compagnies associées
            $("#box_compagnie").show();
            $.ajax({
                url: "/production/get_compagnies/",
                method: "GET",
                data: {
                    type_id: selectedTypeId,
                    compagnie_id: selectedCompagnieId
                },
                success: function (response) {
                    const compagnieSelect = $("#compagnie_id");
                    compagnieSelect.empty().append('<option value="">Choisir</option>');

                    // Ajouter les options retournées par l'API
                    response.compagnies.forEach(function (compagnie) {
                        compagnieSelect.append(`<option value="${compagnie.id}">${compagnie.nom}</option>`);
                    });
                },
                error: function () {
                    alert("Une erreur est survenue lors du chargement des compagnies.");
                }
            });
        } else {
            // Réinitialiser si aucun type n'est sélectionné
            $("#box_compagnie").hide();
            $("#compagnie_id").empty().append('<option value="">Choisir</option>');
        }
    });

    // Rendre le champ "compagnie_id" non obligatoire si la liste est masquée
    $("form").on("submit", function () {
        if ($("#box_compagnie").is(":hidden")) {
            $("#compagnie_id").prop("required", false);
        } else {
            $("#compagnie_id").prop("required", true);
        }
    });

    $(document).on("keyup change", "#modal-police .calculs_marchandise_montant_police", function (event) {

        if (event.which == 13) {
            event.preventDefault();
        }

        calculer_montant_marchandise_police();

    });

    function calculer_montant_marchandise_police() {

        // Récupération des valeurs saisies
        let valeur_assuree = parseInt($('#modal-police #valeur_assuree').val().replaceAll(' ', ''));
        let taux_risque_ordinaire = parseInt($('#modal-police #taux_risque_ordinaire').val().replaceAll(' ', ''));
        let taux_risque_guerre = parseInt($('#modal-police #taux_risque_guerre').val().replaceAll(' ', ''));
        let taux_supprime = parseInt($('#modal-police #taux_supprime').val().replaceAll(' ', ''));
        let taux_reduction_commerciale = parseInt($('#modal-police #taux_reduction_commerciale').val().replaceAll(' ', ''));
        let taux_taxe = parseInt($('#modal-police #taux_taxe').val().replaceAll(' ', ''));
        let accessoires = parseInt($('#modal-police #accessoires').val().replaceAll(' ', ''));
        let autres_frais = parseInt($('#modal-police #autres_frais').val().replaceAll(' ', ''));

        if (isNaN(valeur_assuree)) { valeur_assuree = 0; }
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

        $('#modal-police #prime_risque_ordinaire').val(prime_risque_ordinaire);
        $('#modal-police #prime_risque_guerre').val(prime_risque_guerre);
        $('#modal-police #prime_supprime').val(prime_supprime);
        $('#modal-police #prime_brut').val(prime_brut);
        $('#modal-police #prime_reduction').val(prime_reduction);
        $('#modal-police #total_taxe').val(total_taxe);
        $('#modal-police #prime_ttc_mar').val(prime_ttc_mar);
    }

    $(document).on("keyup change", "#modal-marchandise_add .calculs_add_marchandise_montant_police", function (event) {

        if (event.which == 13) {
            event.preventDefault();
        }

        calculer_montant_add_marchandise_police();

    });

    function calculer_montant_add_marchandise_police() {

        // Récupération des valeurs saisies
        let valeur_assuree = parseInt($('#modal-marchandise_add #valeur_assuree').val().replaceAll(' ', ''));
        let taux_risque_ordinaire = parseInt($('#modal-marchandise_add #taux_risque_ordinaire').val().replaceAll(' ', ''));
        let taux_risque_guerre = parseInt($('#modal-marchandise_add #taux_risque_guerre').val().replaceAll(' ', ''));
        let taux_supprime = parseInt($('#modal-marchandise_add #taux_supprime').val().replaceAll(' ', ''));
        let taux_reduction_commerciale = parseInt($('#modal-marchandise_add #taux_reduction_commerciale').val().replaceAll(' ', ''));
        let taux_taxe = parseInt($('#modal-marchandise_add #taux_taxe').val().replaceAll(' ', ''));
        let accessoires = parseInt($('#modal-marchandise_add #accessoires').val().replaceAll(' ', ''));
        let autres_frais = parseInt($('#modal-marchandise_add #autres_frais').val().replaceAll(' ', ''));

        if (isNaN(valeur_assuree)) { valeur_assuree = 0; }
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

        $('#modal-marchandise_add #prime_risque_ordinaire').val(prime_risque_ordinaire);
        $('#modal-marchandise_add #prime_risque_guerre').val(prime_risque_guerre);
        $('#modal-marchandise_add #prime_supprime').val(prime_supprime);
        $('#modal-marchandise_add #prime_brut').val(prime_brut);
        $('#modal-marchandise_add #prime_reduction').val(prime_reduction);
        $('#modal-marchandise_add #total_taxe').val(total_taxe);
        $('#modal-marchandise_add #prime_ttc_mar').val(prime_ttc_mar);
    }

    $(document).on("keyup change", "#modal-modification_marchandise .calculs_marchandise_montant_police_modification", function (event) {

        if (event.which == 13) {
            event.preventDefault();
        }

        calculer_montant_marchandise_modification();

    });

    function calculer_montant_marchandise_modification() {

        let valeur_assuree = parseInt($('#modal-modification_marchandise #valeur_assuree_modification').val().replaceAll(' ', ''));
        let taux_risque_ordinaire = parseInt($('#modal-modification_marchandise #taux_risque_ordinaire_modification').val().replaceAll(' ', ''));
        let taux_risque_guerre = parseInt($('#modal-modification_marchandise #taux_risque_guerre_modification').val().replaceAll(' ', ''));
        let taux_supprime = parseInt($('#modal-modification_marchandise #taux_supprime_modification').val().replaceAll(' ', ''));
        let taux_reduction_commerciale = parseInt($('#modal-modification_marchandise #taux_reduction_commerciale_modification').val().replaceAll(' ', ''));
        let taux_taxe = parseInt($('#modal-modification_marchandise #taux_taxe_modification').val().replaceAll(' ', ''));
        let accessoires = parseInt($('#modal-modification_marchandise #accessoires_modification').val().replaceAll(' ', ''));
        let autres_frais = parseInt($('#modal-modification_marchandise #autres_frais_modification').val().replaceAll(' ', ''));

        if (isNaN(valeur_assuree)) { valeur_assuree = 0; }
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

        $('#modal-modification_marchandise #prime_risque_ordinaire_modification').val(prime_risque_ordinaire);
        $('#modal-modification_marchandise #prime_risque_guerre_modification').val(prime_risque_guerre);
        $('#modal-modification_marchandise #prime_supprime_modification').val(prime_supprime);
        $('#modal-modification_marchandise #prime_brut_modification').val(prime_brut);
        $('#modal-modification_marchandise #prime_reduction_modification').val(prime_reduction);
        $('#modal-modification_marchandise #total_taxe_modification').val(total_taxe);
        $('#modal-modification_marchandise #prime_ttc_mar_modification').val(prime_ttc_mar);
    }

    const searchInput = $('#search_all');
    const suggestionsBox = $('#suggestions');
    const searchError = $('#search-error');
    const searchForm = $('#search-form');

    let selectedDetailsUrl = '';

    searchInput.on('input', function () {
        const query = $(this).val().trim();

        if (query.length < 3) {
            searchError.text("Saisissez au moins 3 caractères").removeClass('d-none');
            suggestionsBox.addClass('d-none');
            selectedDetailsUrl = '';
            return;
        }

        searchError.addClass('d-none');

        $.ajax({
            url: `/api/suggestions`,
            method: 'GET',
            data: { numero: query },
            success: function (data) {
                displaySuggestions(data);
            },
            error: function (xhr, status, error) {
                console.error('Erreur lors de la récupération des suggestions:', error);
            }
        });
    });

    function displaySuggestions(data) {
        if (data.length > 0) {
            suggestionsBox.empty();

            $.each(data, function (index, item) {
                const suggestion = $(`
                    <div class="list-group-item list-group-item-action suggestion-item" style="cursor:pointer;">
                        N° Police : <strong>${item.numero_police}</strong> / Client : <strong>${item.client_nom}</strong>
                    </div>
                `).on('click', function () {
                    searchInput.val(item.numero_police);
                    suggestionsBox.addClass('d-none');
                    selectedDetailsUrl = item.details_url; // 🔹 Enregistre l'URL sélectionnée
                });

                suggestionsBox.append(suggestion);
            });

            suggestionsBox.removeClass('d-none');
        } else {
            suggestionsBox.html('<div class="list-group-item">Aucun résultat</div>');
            suggestionsBox.removeClass('d-none');
        }
    }

    $(document).on('click', function (e) {
        if (!suggestionsBox.is(e.target) && !searchInput.is(e.target) && suggestionsBox.has(e.target).length === 0) {
            suggestionsBox.addClass('d-none');
        }
    });

    // 🔹 Redirection vers l'URL de détail lors du clic sur "Rechercher"
    searchForm.on('submit', function (e) {
        e.preventDefault();

        const query = searchInput.val().trim();

        if (query.length < 3) {
            searchError.text("Saisissez au moins 3 caractères").removeClass('d-none');
            return;
        }

        if (selectedDetailsUrl) {
            window.location.href = selectedDetailsUrl;
        } else {
            // Message si aucune suggestion n’a été sélectionnée
            searchError.text("Veuillez sélectionner une suggestion avant de rechercher.").removeClass('d-none');
        }
    });

    // Soumission du formulaire : vérifier les 3 caractères
    searchForm.on('submit', function (e) {
        const query = searchInput.val().trim();
        if (query.length < 3) {
            e.preventDefault();
            searchError.text("Saisissez au moins 3 caractères").removeClass('d-none');
        }
    });

    function toggleReadonlyFields(prefix) {
        var valeurAssuree = parseFloat($('#valeur_assuree' + prefix).val().replace(/,/g, ''));
        var readonlyFields = isNaN(valeurAssuree) || valeurAssuree === 0;

        var fieldsToReadonly = $(
            '#taux_risque_ordinaire' + prefix + ', ' +
            '#taux_risque_guerre' + prefix + ', ' +
            '#taux_supprime' + prefix + ', ' +
            '#taux_reduction_commerciale' + prefix + ', ' +
            '#taux_taxe' + prefix + ', ' +
            '#accessoires' + prefix + ', ' +
            '#autres_frais' + prefix
        );

        fieldsToReadonly.prop('readonly', readonlyFields);

        if (readonlyFields) {
            fieldsToReadonly.addClass('readonly-field');
            // Important : Vider les champs ici pour effacer les valeurs affichées
            fieldsToReadonly.val('');
        } else {
            fieldsToReadonly.removeClass('readonly-field');
        }
    }

    // Initialisation et gestion des événements pour les deux formulaires
    toggleReadonlyFields("");
    $('#valeur_assuree').on('input', function() {
        toggleReadonlyFields("");
    });

    toggleReadonlyFields("_modification");
    $('#valeur_assuree_modification').on('input', function() {
        toggleReadonlyFields("_modification");
    });

    // Récupérer les éléments
    const $yesRadio = $("#yes_garantie_modification");
    const $noRadio = $("#no_garantie_modification");
    const $garantieTableBody = $("#table_garantie_police_modification tbody");
    const $garantieTableContainer = $("#test_garantie_modification");
    const $formuleBlock = $("#formule_block_modification");

    // Fonction pour afficher ou masquer le tableau des garanties et le champ de formule
    function toggleGarantieTable() {
        if ($yesRadio.is(":checked")) {
            // Afficher le tableau et le champ de formule si OUI est sélectionné
            $garantieTableContainer.show();
            $formuleBlock.show();
        } else {
            // Si NON est sélectionné, vider le contenu du tableau, masquer le conteneur et le champ de formule
            $garantieTableBody.empty();
            $garantieTableContainer.hide();
            $formuleBlock.hide();
        }
    }

    // Écouter les événements de clic sur les boutons radio
    $yesRadio.on("click", toggleGarantieTable);
    $noRadio.on("click", toggleGarantieTable);

    // Initialiser l'état du tableau et du champ de formule au chargement de la page
    toggleGarantieTable();

});

//TODO FABRICE Partie 2
$(document).ready(function () {
    function getCSRFToken() {
        return $("input[name=csrfmiddlewaretoken]").val();
    }

    if (!Object.keys) {
      Object.keys = (function () {
        'use strict';
        var hasOwnProperty = Object.prototype.hasOwnProperty,
            hasDontEnumBug = !({ toString: null }).propertyIsEnumerable('toString'),
            dontEnums = [
              'toString',
              'toLocaleString',
              'valueOf',
              'hasOwnProperty',
              'isPrototypeOf',
              'propertyIsEnumerable',
              'constructor'
            ],
            dontEnumsLength = dontEnums.length;

        return function (obj) {
          if (typeof obj !== 'object' && (typeof obj !== 'function' || obj === null)) {
            throw new TypeError('Object.keys called on non-object');
          }

          var result = [], prop, i;

          for (prop in obj) {
            if (hasOwnProperty.call(obj, prop)) {
              result.push(prop);
            }
          }

          if (hasDontEnumBug) {
            for (i = 0; i < dontEnumsLength; i++) {
              if (hasOwnProperty.call(obj, dontEnums[i])) {
                result.push(dontEnums[i]);
              }
            }
          }
          return result;
        };
      }());
    }

    var my_noty;//variale global pour pouvoir le fermer de popup de l'extérieur
    function notifySuccess(message, fnCallback) {
        my_noty = noty({
            text: message,
            type: 'success',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'OK', onClick: function ($noty) {

                        if (typeof fnCallback === 'function') fnCallback();

                        $noty.close();
                    }
                }
            ]
        });
    }

    function notifyWarning(message, fnCallback) {
        if (my_noty) {
            my_noty.close();
        }

        my_noty = noty({
            text: message,
            type: 'warning',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'OK', onClick: function ($noty) {

                        if (typeof fnCallback === 'function') fnCallback();

                        $noty.close();
                    }
                }
            ]
        });

    }

    function notifyError(message, fnCallback) {
        my_noty = noty({
            text: message,
            type: 'error',
            dismissQueue: true,
            layout: 'center',
            theme: 'defaultTheme',
            buttons: [
                {
                    addClass: 'btn btn-primary', text: 'OK', onClick: function ($noty) {

                        if (typeof fnCallback === 'function') fnCallback();

                        $noty.close();
                    }
                }
            ]
        });
    }

    // Fonction utilitaire : Affiche un tab et rend les champs obligatoires
    function afficherOngletAvecChamps(tabSelector, champSelector) {
        $(tabSelector).removeClass('d-none');
        $(champSelector).attr('required', true);
    }

    // Liste des onglets dynamiques
    const ongletsDynamiques = ['#risque-tab', '#aliment-tab', '#vehicule-tab', '#marchandise-tab'];
    const champsDynamiques = ['.marchandise_champ_obligatoire', '.vehicule_champ_obligatoire'];

    // Liste des onglets fixes avec leurs champs obligatoires
    const ongletsFixes = [
        { tab: '#garantie-tab', champ: '.garantie_champ_obligatoire' },
        { tab: '#intermediaire-tab', champ: '.intermediaire_champ_obligatoire' },
        { tab: '#general-tab' },
        { tab: '#facturation-tab' },
        { tab: '#prime-tab' },
    ];

    // *** Initialisation ***
    // Masquer les onglets dynamiques
    $(ongletsDynamiques.join(', ')).addClass('d-none');
    $(champsDynamiques.join(', ')).removeAttr('required');
    $('#table_liste_aliment tbody').empty();

    // Afficher les onglets fixes
    ongletsFixes.forEach(onglet => {
        $(onglet.tab).removeClass('d-none');
        if (onglet.champ) {
            $(onglet.champ).attr('required', true); // rendre les champs obligatoires
        }
    });

    // *** Changement de produit ***
    $('#produit').on('change', function () {
        let produit_id = $(this).val();

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

        // Si un produit est sélectionné
        $.ajax({
            type: 'get',
            url: '/production/produit/' + produit_id + '/sous-menu',
            success: function (produit) {
                produit_code = produit[0].fields.code;

                // Réinitialiser les dynamiques
                $(ongletsDynamiques.join(', ')).addClass('d-none');
                $(champsDynamiques.join(', ')).removeAttr('required');
                $('#table_liste_aliment tbody').empty();

                // Réafficher les onglets fixes + champs required
                ongletsFixes.forEach(onglet => {
                    $(onglet.tab).removeClass('d-none');
                    if (onglet.champ) {
                        $(onglet.champ).attr('required', true);
                    }
                });

                // Logique produit_code : affichage dynamique
                if (produit_code == 10001) { // Mono-Véhicule
                    afficherOngletAvecChamps('#vehicule-tab', '.vehicule_champ_obligatoire');
                } else if (produit_code == 10002) { // Flotte-Auto
                    afficherOngletAvecChamps('#aliment-tab', '.mod_aliment_champ_obligatoire');
                } else if (produit_code == 50001 || produit_code == 50002) { // Produits marchandise
                    afficherOngletAvecChamps('#marchandise-tab', '.marchandise_champ_obligatoire');
                } else {
                    $('#risque-tab').removeClass('d-none');
                }
            },
            error: function () {
                console.error('Erreur lors du chargement des sous-menus.');
            }
        });
    });

    //Récupération des polices
    function chargementPoliceCompagnieTable(compagnieId) {
        $("#table_polices_compagnie tbody").empty();
        $("#com_total_ht").text("");
        $("#com_total_com_courtage").text("");
        $("#btn_save_portefeuille_compagnie").prop("disabled", true);

        $('#message-error').text('').hide();
        $('#message-warning').text('').hide();

        if (!compagnieId) {
            $("#polices_compagnie").hide();
            return;
        }

        $.ajax({
            url: "/analysecontrole/get_client_by_compagnie/",
            type: "GET",
            data: { compagnie_id: compagnieId },
            success: function (data) {
                if (data && data.polices_par_compagnie) {
                    $("#polices_compagnie").show();
                    $("#table_polices_compagnie tbody").empty();

                    let total_ht = 0;
                    let total_com_courtage = 0;

                    for (const [compagnie, details] of Object.entries(data.polices_par_compagnie)) {
                        let polices = details.polices; // Extraire le tableau de polices

                        let compagnieHeader = `
                            <tr>
                                <td colspan="5" class="fw-bold text-primary">${compagnie}</td>
                                <td class="fw-bold text-inov_green">TOTAL</td>
                                <td class="fw-bold text-inov_green">${details.compagnie_total_ht}</td>
                                <td class="fw-bold text-inov_green">${details.compagnie_com_courtage}</td>
                            </tr>
                        `;
                        $("#table_polices_compagnie tbody").append(compagnieHeader);

                        polices.forEach(police => {
                            total_ht += parseFloat(police.prime_ht.replace(/\s/g, '').replace(',', '.')) || 0;
                            total_com_courtage += parseFloat(police.commission_courtage.replace(/\s/g, '').replace(',', '.')) || 0;

                            let badgeClass = police.statut.includes("A renouveler") ? "badge-warning" :
                                             police.statut.includes("NON renouvelé") ? "badge-danger" :
                                             police.statut.includes("Résilié") ? "badge-yellow" :
                                             "badge-success";

                            let row = `
                                <tr>
                                    <td>${police.nom} ${police.prenoms}</td>
                                    <td>${police.numero}</td>
                                    <td>${police.date_fin_effet}</td>
                                    <td><span class="badge ${badgeClass}">${police.statut}</span></td>
                                    <td>${police.date_creation}</td>
                                    <td>${police.date_resiliation}</td>
                                    <td>${police.prime_ht}</td>
                                    <td>${police.commission_courtage}</td>
                                </tr>
                            `;
                            $("#table_polices_compagnie tbody").append(row);
                        });
                    }

                    $("#com_total_ht").text(total_ht.toLocaleString("fr-FR"));
                    $("#com_total_com_courtage").text(total_com_courtage.toLocaleString("fr-FR"));
                    $("#btn_save_portefeuille_compagnie").prop("disabled", false);
                }
            }
        });
    }

    $("#compagnie").change(function () {
        let compagnieId = $(this).find(":selected").data("compagnie_id");

        if (compagnieId) {
            chargementPoliceCompagnieTable(compagnieId);
        } else {
            $("#polices_compagnie").hide(); // Masquer le bloc si aucun compercial n'est sélectionnée
        }
    });

    //Récupération des polices
    function chargementPoliceCommercialTable(commercialId) {
        $("#table_polices_commercial tbody").empty();
        $("#com_total_ht").text("");
        $("#com_total_com_courtage").text("");
        $("#btn_save_portefeuille_commercial").prop("disabled", true);

        $('#message-error').text('').hide();
        $('#message-warning').text('').hide();

        if (!commercialId) {
            $("#polices_commercial").hide();
            return;
        }

        $.ajax({
            url: "/analysecontrole/get_client_by_commercial/",
            type: "GET",
            data: { commercial_id: commercialId },
            success: function (data) {
                if (data && data.polices_par_commercial) {
                    $("#polices_commercial").show();
                    $("#table_polices_commercial tbody").empty();

                    let total_ht = 0;
                    let total_com_courtage = 0;

                    for (const [commercial, details] of Object.entries(data.polices_par_commercial)) {
                        let polices = details.polices; // Extraire le tableau de polices

                        let commercialHeader = `
                            <tr>
                                <td colspan="5" class="fw-bold text-primary">${commercial}</td>
                                <td class="fw-bold text-inov_green">TOTAL</td>
                                <td class="fw-bold text-inov_green">${details.commercial_total_ht}</td>
                                <td class="fw-bold text-inov_green">${details.commercial_com_courtage}</td>
                            </tr>
                        `;
                        $("#table_polices_commercial tbody").append(commercialHeader);

                        polices.forEach(police => {
                            total_ht += parseFloat(police.prime_ht.replace(/\s/g, '').replace(',', '.')) || 0;
                            total_com_courtage += parseFloat(police.commission_courtage.replace(/\s/g, '').replace(',', '.')) || 0;

                            let badgeClass = police.statut.includes("A renouveler") ? "badge-warning" :
                                             police.statut.includes("NON renouvelé") ? "badge-danger" :
                                             police.statut.includes("Résilié") ? "badge-yellow" :
                                             "badge-success";

                            let row = `
                                <tr>
                                    <td>${police.nom} ${police.prenoms}</td>
                                    <td>${police.numero}</td>
                                    <td>${police.date_fin_effet}</td>
                                    <td><span class="badge ${badgeClass}">${police.statut}</span></td>
                                    <td>${police.date_creation}</td>
                                    <td>${police.date_resiliation}</td>
                                    <td>${police.prime_ht}</td>
                                    <td>${police.commission_courtage}</td>
                                </tr>
                            `;
                            $("#table_polices_commercial tbody").append(row);
                        });
                    }

                    $("#com_total_ht").text(total_ht.toLocaleString("fr-FR"));
                    $("#com_total_com_courtage").text(total_com_courtage.toLocaleString("fr-FR"));
                    $("#btn_save_portefeuille_commercial").prop("disabled", false);
                }
            }
        });
    }

    $("#commercial").change(function () {
        let commercialId = $(this).find(":selected").data("commercial_id");

        if (commercialId) {
            chargementPoliceCommercialTable(commercialId);
        } else {
            $("#polices_commercial").hide(); // Masquer le bloc si aucun compercial n'est sélectionnée
        }
    });

    //Récupération des polices
    function chargementPoliceBusinessUnitTable(business_unitID) {
        $("#table_polices_business_unit tbody").empty();
        $("#bus_total_ht").text("");
        $("#bus_total_com_courtage").text("");
        $("#btn_save_portefeuille_business_unit").prop("disabled", true);

        $('#message-error').text('').hide();
        $('#message-warning').text('').hide();

        if (!business_unitID) {
            $("#polices_business_unit").hide();
            return;
        }

        $.ajax({
            url: "/analysecontrole/get_client_by_business_unit/",
            type: "GET",
            data: { business_unit_id: business_unitID },
            success: function (data) {
                if (data && data.polices_par_business_unit) {
                    $("#polices_business_unit").show();
                    $("#table_polices_business_unit tbody").empty();

                    let total_ht = 0;
                    let total_com_courtage = 0;

                    for (const [business_unit, details] of Object.entries(data.polices_par_business_unit)) {
                        let polices = details.polices; // Extraire le tableau de polices

                        let business_unitHeader = `
                            <tr>
                                <td colspan="5" class="fw-bold text-primary">${business_unit}</td>
                                <td class="fw-bold text-inov_green">TOTAL</td>
                                <td class="fw-bold text-inov_green">${details.business_unit_total_ht}</td>
                                <td class="fw-bold text-inov_green">${details.business_unit_com_courtage}</td>
                            </tr>
                        `;
                        $("#table_polices_business_unit tbody").append(business_unitHeader);

                        polices.forEach(police => {
                            total_ht += parseFloat(police.prime_ht.replace(/\s/g, '').replace(',', '.')) || 0;
                            total_com_courtage += parseFloat(police.commission_courtage.replace(/\s/g, '').replace(',', '.')) || 0;

                            let badgeClass = police.statut.includes("A renouveler") ? "badge-warning" :
                                             police.statut.includes("NON renouvelé") ? "badge-danger" :
                                             police.statut.includes("Résilié") ? "badge-yellow" :
                                             "badge-success";

                            let row = `
                                <tr>
                                    <td>${police.nom}</td>
                                    <td>${police.numero}</td>
                                    <td>${police.date_fin_effet}</td>
                                    <td><span class="badge ${badgeClass}">${police.statut}</span></td>
                                    <td>${police.date_creation}</td>
                                    <td>${police.date_resiliation}</td>
                                    <td>${police.prime_ht}</td>
                                    <td>${police.commission_courtage}</td>
                                </tr>
                            `;
                            $("#table_polices_business_unit tbody").append(row);
                        });
                    }

                    $("#bus_total_ht").text(total_ht.toLocaleString("fr-FR"));
                    $("#bus_total_com_courtage").text(total_com_courtage.toLocaleString("fr-FR"));
                    $("#btn_save_portefeuille_business_unit").prop("disabled", false);
                }
            }
        });
    }

    $("#business_unit").change(function () {
        let business_unitID = $(this).find(":selected").data("business_unit_id");

        if (business_unitID) {
            chargementPoliceBusinessUnitTable(business_unitID);
        } else {
            $("#polices_business_unit").hide(); // Masquer le bloc si aucun compercial n'est sélectionnée
        }
    });

    //TODO MENU SINISTRE
    $('#list_police_client').hide();
    $('#default_page').show();
    $('#formulaire_page').hide();

    // using jQuery
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

    $('#btn_search_client_police').click(function() {
        let formulaire = $('#form_choose_client');
        let href = formulaire.attr('action');
        var ClientId = $('#search_client_id').val().toUpperCase();
        var NumeroPolice = $('#search_numero_police').val().toUpperCase();
        var $tableBody = $('#table_liste_police tbody');
        $tableBody.empty();
        $('#loading_gif').show();

        $.ajax({
            url: href,
            type: 'POST',
            data: {
                'search_client_id': ClientId,
                'search_numero_police': NumeroPolice,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            dataType: 'json',
            success: function(data) {
                $('#loading_gif').hide();
                if (data.success) {
                    if (data.polices && data.polices.length > 0) {

                        // Formatter les données pour DataTable
                        var formattedData = data.polices.map(function(police) {
                            return [
                                '<input type="radio" name="selected_police" value="' + police.id + '">',
                                police.numero,
                                police.produit,
                                police.assureur,
                                police.date_debut,
                                police.date_echeance
                            ];
                        });

                        $('#list_police_client').show();
                        $('.error_box_aliment_not_found').hide();

                        if (!$.fn.DataTable.isDataTable('#table_liste_police')) {
                            // Initialiser DataTable
                            $('#table_liste_police').DataTable({
                                "language": {
                                    "url": "../../static/admin_custom/js/French.json"
                                },
                                lengthMenu: [
                                    [100, 250, 500, 1000, -1], [100, 250, 500, 1000, "Tout"]
                                ],
                                paging: true,
                                searching: true,
                                lengthChange: true,
                                bSort: false,
                                data: formattedData, // Utiliser les données formatées
                                columns: [ // Définir les colonnes
                                    { title: "" },
                                    { title: "Numéro" },
                                    { title: "Produit" },
                                    { title: "Assureur" },
                                    { title: "Date début" },
                                    { title: "Date échéance" }
                                ]
                            });
                        } else {
                            // Recharger les données
                            $('#table_liste_police').DataTable().clear().rows.add(formattedData).draw();
                        }

                    } else {
                        $('#list_police_client').hide();
                        $('.error_box_aliment_not_found').text('Aucune police trouvée pour ce client.').show();
                    }
                } else {
                    $('#list_police_client').hide();
                    $('.error_box_aliment_not_found').text(data.message || 'Client non trouvé.').show();
                }
            },
            error: function() {
                $('#loading_gif').hide();
                $('#list_police_client').hide();
                $('.error_box_aliment_not_found').text('Erreur lors de la recherche.').show();
            }
        });
    });

    // Gestion du bouton 'Continuer'
    $('#btn_confirm_selected_police_client').click(function() {
        var selectedPoliceId = $('input[name=selected_police]:checked').val();
        var police_id = selectedPoliceId;
        if (selectedPoliceId) {
            // Vider le tableau et les champs
            $('#search_client_id').val('');
            $('#search_numero_police').val('');
            $('#table_liste_police tbody').empty();

            // Cacher le tableau
            $('#list_police_client').hide();

            // Appel AJAX pour récupérer les informations de la police
            $.ajax({
                url: "/sinistre/recuperer_information_police/",
                type: "GET",
                data: {
                    police_id: police_id
                },
                success: function (response) {
                    console.log(response);
                    $('#default_page').hide();
                    $('#formulaire_page').show().html(response);

                    console.log('Lancement du chargement des intervenants');
                    // Appel AJAX pour récupérer l'intervenant par défaut de la police
                    setTimeout(() => {
                        // Requête 2 : récupérer l’intervenant
                        $.ajax({
                            url: "/sinistre/recuperer_intervenant_police/",
                            type: "GET",
                            data: {
                                police_id: selectedPoliceId
                            },
                            success: function (response) {
                                console.log("Intervenant :", response);

                                if (response.success && response.data.length > 0) {
                                    const tbody = $("#table_intervenant_sinistre tbody");
                                    tbody.empty(); // Corriger les doublons

                                    response.data.forEach((row, index) => {
                                        const isFirst = index === 0;
                                        tbody.append(`
                                            <tr data-id="${row.id}">
                                                <td>
                                                    <button class="btn btn-danger btn-sm btn-delete-intervenant" type="button" ${isFirst ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
                                                        <i class="fa fa-trash-o"></i>
                                                    </button>
                                                </td>
                                                <td>${row.nom || ''}</td>
                                                <td>${row.prenoms || ''}</td>
                                                <td>${row.type_intervenant || ''}</td>
                                                <td>${row.portable || ''}</td>
                                                <td>${row.email || ''}</td>
                                                <td>${row.boite_postale || ''}</td>
                                                <td>${row.ville || ''}</td>
                                            </tr>
                                        `);
                                    });
                                } else {
                                    console.warn("Aucun intervenant ou réponse invalide :", response.message || response.error);
                                }
                            },
                            error: function (xhr, status, error) {
                                console.error("Erreur lors de la récupération de l'intervenant :", error);
                            }
                        });
                    }, 100);
                },
                error: function (xhr, status, error) {
                    console.error("Erreur lors du chargement des information de la police :", error);
                }
            });

            $('#modal_choose_client').modal('hide');
        } else {
            notifyWarning("Veuillez sélectionner une police.");
        }
    });

    $('#btn_save_sinistre_intervenant').on('click', function () {
        // Supprimer les erreurs précédentes
        $('.intervenant_champ_obligatoire').removeClass('is-invalid').removeClass('is-valid');
        $('#intervenant-modal-error').text('').hide();
        $('#intervenant-modal-warning').text('').hide();
        $('#intervenant-modal-success').text('').hide();

        // Valider les champs obligatoires
        let valide = true;
        $('.intervenant_champ_obligatoire').each(function () {
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
            $('#intervenant-modal-error').text('Veuillez remplir tous les champs obligatoires.').show();
            setTimeout(() => $('#intervenant-modal-error').fadeOut(), 5000);
            return;
        }

        // Récupérer les données du formulaire
        const formData = new FormData($('#form_add_sinistre_intervenant')[0]);

        // Requête Ajax pour envoyer les données au backend
        $.ajax({
            url: '/sinistre/ajout-intervenant-sinistre/',
            type: 'POST',
            data: formData,
            processData: false, // Indique que nous envoyons un FormData
            contentType: false, // Pour ne pas encoder les données
            success: function (response) {
                if (response.success) {
                    // Afficher le message de succès
                    $("#intervenant-modal-success").text(response.message).show().delay(5000).fadeOut();

                    // Mettre à jour le tableau avec les nouvelles données
                    const tbody = $("#table_intervenant_sinistre tbody");
                    tbody.empty(); // <-- ✅ Corrige les doublons

                    response.data.forEach((row, index) => {
                        const isFirst = index === 0;
                        tbody.append(`
                            <tr data-id="${row.id}">
                                <td>
                                    <button class="btn btn-danger btn-sm btn-delete-intervenant" type="button" ${isFirst ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
                                        <i class="fa fa-trash-o"></i>
                                    </button>
                                </td>
                                <td>${row.nom || ''}</td>
                                <td>${row.prenoms || ''}</td>
                                <td>${row.type_intervenant || ''}</td>
                                <td>${row.portable || ''}</td>
                                <td>${row.email || ''}</td>
                                <td>${row.boite_postale || ''}</td>
                                <td>${row.ville || ''}</td>
                            </tr>
                        `);
                    });

                    // Réinitialiser tous les champs du formulaire
                    $("#form_add_sinistre_intervenant").trigger("reset");
                    $("#form_add_sinistre_intervenant select").each(function() {
                        $(this).prop('selectedIndex', 0).trigger('change');
                    });
                    $('.intervenant_champ_obligatoire').removeClass('is-valid').removeClass('is-invalid');

                } else {
                    // Afficher un message d'avertissement
                    $("#intervenant-modal-warning").text(response.message).show().delay(5000).fadeOut();
                }
            },
            error: function (xhr) {
                // Gérer les erreurs 500 ou autres erreurs inattendues
                const response = xhr.responseJSON;
                if (xhr.status === 500) {
                    $("#intervenant-modal-error").text(response?.message || "Une erreur interne du serveur est survenue. Veuillez réessayer plus tard.").show().delay(5000).fadeOut();
                } else if (xhr.status === 400) {
                    $("#intervenant-modal-warning").text(response?.message || "Erreur dans les données soumises. Veuillez vérifier votre fichier.").show().delay(5000).fadeOut();
                } else {
                    $("#intervenant-modal-error").text(response?.message || "Une erreur inattendue est survenue. Veuillez réessayer.").show().delay(5000).fadeOut();
                }
            },
        });
    });

    $(document).on('click', '.btn-delete-intervenant', function () {
        const row = $(this).closest('tr');
        const id = row.data('id');

        $.ajax({
            url: `/sinistre/supprimer_intervenant/${id}/`,
            type: 'POST',
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            success: function (response) {
                if (response.success) {
                    row.remove(); // Supprime la ligne
                } else {
                    console.error(response.error || 'Erreur lors de la suppression.');
                }
            },
            error: function () {
                console.error('Erreur de communication avec le serveur.');
            }
        });
    });

    // Fonction pour vider la session des garanties liées à la circonstance
    function resetGarantiesSession() {
        $.ajax({
            url: "/sinistre/get_garanties_by_circonstance_clean/",
            type: "GET",
            success: function (response) {
                if (response.success) {
                    $("#table_garantie_sinistre tbody").empty();
                    $("#table_provision_sinistre_container tbody").empty();
                    $.ajax({
                        url: "/sinistre/recuperer_garantie_session/",
                        type: "GET",
                        success: function (data) {
                            console.log('Initialisation de garanties');
                            $("#liste_garantie_session").html('<div class="alert alert-info">Aucune garantie disponible.</div>');
                        },
                        error: function (xhr, status, error) {
                            const errorMessage = 'Erreur lors de la récupération des garanties. Veuillez réessayer.';
                            $("#liste_garantie_session").html('<div class="alert alert-danger">' + errorMessage + '</div>');
                        }
                    });
                } else {
                    console.warn("Avertissement :", response.message);
                }
            },
            error: function (xhr, status, error) {
                let messageErreur = "Erreur lors de la réinitialisation des garanties. Veuillez réessayer.";
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.message) {
                        messageErreur = response.message;
                    }
                } catch (e) {
                    // Ignorer le parsing si la réponse n'est pas JSON
                }
                console.error("Erreur :", messageErreur);
            }
        });
    }

    //gestion selection circonstance
    function manage_circonstance_change() {

        resetGarantiesSession(); // ✅ Nettoyage session avant tout

        let circonstance_id = parseInt($('#form_add_sinistre_gestionnaire #circonstance_id').val());

        $("#modal-sinistre_garantie #table_add_sinistre_garantie tbody").empty();
        $('#garantie-message-warning').hide();

        if (circonstance_id) {
            $("#form_add_sinistre_gestionnaire #btn_ajout_garantie").show();

            $.ajax({
                url: "/sinistre/get_garanties_by_circonstance/",
                type: "GET",
                data: { circonstance_id: circonstance_id },
                success: function (data) {
                    if (data && data.garanties && data.garanties.length > 0) {
                        data.garanties.forEach((garantie, index) => {
                            let row = `
                                <tr>
                                    <td style="vertical-align:middle;">
                                        <input type="checkbox" class="form-control garantie-checkbox" name="garantie_${garantie.id}" value="${garantie.id}" style="width: 1rem; height: 1.25rem;">
                                    </td>
                                    <td style="vertical-align:middle;">${garantie.nom}</td>
                                    <td style="vertical-align:middle;padding:5px;">
                                        <input type="text" class="form-control form-control-sm franchise-input" name="franchise_${garantie.id}" value="" onkeypress="isInputNumber(event)" oninput="formatMontant(this)" disabled>
                                    </td>
                                    <td style="vertical-align:middle;padding:5px;">
                                        <input type="text" class="form-control form-control-sm capital-input" name="capital_${garantie.id}" value="" onkeypress="isInputNumber(event)" oninput="formatMontant(this)" disabled>
                                    </td>
                                </tr>
                            `;
                            $("#modal-sinistre_garantie #table_add_sinistre_garantie tbody").append(row);
                        });
                    } else {
                        $('#garantie-message-warning').text('Aucune garantie trouvée pour cette circonstance.').show();
                    }
                },
                error: function (xhr, status, error) {
                    const errorMessage = 'Erreur lors de la récupération des garanties. Veuillez réessayer.';
                    try {
                        const errorResponse = JSON.parse(xhr.responseText);
                        $('#garantie-message-error').text(errorResponse.error || errorMessage).show();
                    } catch (e) {
                        $('#garantie-message-error').text(errorMessage).show();
                    }
                    setTimeout(() => $('#garantie-message-error').fadeOut(5000), 500);
                },
            });

            $('#btn_save_sinistre_garantie').on('click', function () {
                const garanties = [];

                $('#table_add_sinistre_garantie tbody tr').each(function () {
                    const checkbox = $(this).find('.garantie-checkbox');
                    if (checkbox.is(':checked')) {
                        const garantieId = checkbox.val();
                        const nom = $(this).find('td:nth-child(2)').text().trim();
                        const franchise = $(this).find('.franchise-input').val();
                        const capital = $(this).find('.capital-input').val();

                        garanties.push({
                            id: garantieId,
                            nom: nom,
                            franchise: franchise,
                            capital: capital
                        });
                    }
                });

                if (garanties.length === 0) {
                    $("#garantie-modal-warning").text("Veuillez cocher au moins une garantie.").show().delay(5000).fadeOut();
                    return;
                }

                $.ajax({
                    url: '/sinistre/ajout-garantie-sinistre/',
                    type: 'POST',
                    data: JSON.stringify({ garanties: garanties }),
                    contentType: 'application/json',
                    success: function (response) {

                        $.ajax({
                            url: "/sinistre/recuperer_garantie_session/",
                            type: "GET",
                            success: function (data) {
                                console.log('Afficher le contenu HTML des garantie');
                                $("#liste_garantie_session").html(data);
                            },
                            error: function (xhr, status, error) {
                                const errorMessage = 'Erreur lors de la récupération des garanties. Veuillez réessayer.';
                                $("#liste_garantie_session").html('<div class="alert alert-danger">' + errorMessage + '</div>');
                            }
                        });

                        if (response.success) {
                            $("#garantie-modal-success").text(response.message).show().delay(5000).fadeOut();

                            const tbody = $("#table_garantie_sinistre tbody");
                            tbody.empty();

                            response.data.forEach((row) => {
                                tbody.append(`
                                    <tr data-id="${row.id}">
                                        <td>
                                            <button class="btn btn-danger btn-sm btn-delete-garantie" type="button">
                                                <i class="fa fa-trash-o"></i>
                                            </button>
                                        </td>
                                        <td>${row.nom || ''}</td>
                                        <td>${row.franchise || ''}</td>
                                        <td>${row.capital || ''}</td>
                                        <td>${row.mouvement || ''}</td>
                                        <td>${row.date_ajout || ''}</td>
                                    </tr>
                                `);
                            });

                            $("#form_add_sinistre_garantie").trigger("reset");

                        } else {
                            $("#garantie-modal-warning").text(response.message).show().delay(5000).fadeOut();
                        }
                    },
                    error: function (xhr) {
                        const response = xhr.responseJSON;
                        const message = response?.message || "Une erreur est survenue. Veuillez réessayer.";
                        const target = xhr.status === 400 ? "#garantie-modal-warning" : "#garantie-modal-error";
                        $(target).text(message).show().delay(5000).fadeOut();
                    }
                });
            });

            $(document).on('click', '.btn-delete-garantie', function () {
                const row = $(this).closest('tr');
                const id = row.data('id');

                $.ajax({
                    url: `/sinistre/supprimer_garantie/${id}/`,
                    type: 'POST',
                    headers: { 'X-CSRFToken': getCookie('csrftoken') },
                    success: function (response) {
                        if (response.success) {
                            row.remove(); // Supprime la ligne
                            $.ajax({
                                url: "/sinistre/recuperer_garantie_session/",
                                type: "GET",
                                success: function (data) {
                                    console.log('Afficher le contenu HTML des garantie');
                                    $("#liste_garantie_session").html(data);
                                },
                                error: function (xhr, status, error) {
                                    const errorMessage = 'Erreur lors de la récupération des garanties. Veuillez réessayer.';
                                    $("#liste_garantie_session").html('<div class="alert alert-danger">' + errorMessage + '</div>');
                                }
                            });
                        } else {
                            console.error(response.error || 'Erreur lors de la suppression.');
                        }
                    },
                    error: function () {
                        console.error('Erreur de communication avec le serveur.');
                    }
                });
            });

        }
        else {
            $("#form_add_sinistre_gestionnaire #btn_ajout_garantie").hide();
            console.log('circonstance non choisie');
        }
    }

    manage_circonstance_change();

    $(document).on('change', "#form_add_sinistre_gestionnaire #circonstance_id", function () {

         manage_circonstance_change();

    });

    $(document).on('click', '#btn_save_mouvement_sinistre', function () {
        let mouvement = $('#mouvement');
        let motif = $('#motif');
        let sinistre_id = $('#sinistre_id').val();

        let champsValides = true;

        // Réinitialiser les bordures
        mouvement.removeClass('is-invalid');
        motif.removeClass('is-invalid');

        // Vérifier mouvement
        if (!mouvement.val()) {
            mouvement.addClass('is-invalid');
            champsValides = false;
        }

        // Vérifier motif
        if (!motif.val()) {
            motif.addClass('is-invalid');
            champsValides = false;
        }

        if (!champsValides) {
            notifyWarning("Veuillez remplir tous les champs obligatoires.");
            return;
        }

        // Redirection vers l'URL Django
        let url = `/sinistre/mouvement_sinistre/${sinistre_id}/${motif.val()}`;
        window.location.href = url;
    });


    function manage_sinistre_change() {
         //Update sinistre
         const selectedSinistreId = $('#sinistre_id').val();

         if (selectedSinistreId) {
            $.ajax({
                   url: "/sinistre/recuperer_intervenant_sinistre/",
                   type: "GET",
                   data: {
                       sinistre_id: selectedSinistreId
                   },
                   success: function (response) {
                       if (response.success && Array.isArray(response.data)) {
                           const tbody = $("#table_intervenant_sinistre tbody");
                           tbody.empty(); // Supprimer les lignes précédentes

                           response.data.forEach((row, index) => {
                               const isFirst = index === 0;
                               tbody.append(`
                                   <tr data-id="${row.id}">
                                       <td>
                                           <button class="btn btn-danger btn-sm btn-delete-intervenant" type="button" ${isFirst ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
                                               <i class="fa fa-trash-o"></i>
                                           </button>
                                       </td>
                                       <td>${row.nom || ''}</td>
                                       <td>${row.prenoms || ''}</td>
                                       <td>${row.type_intervenant || ''}</td>
                                       <td>${row.portable || ''}</td>
                                       <td>${row.email || ''}</td>
                                       <td>${row.boite_postale || ''}</td>
                                       <td>${row.ville || ''}</td>
                                   </tr>
                               `);
                           });
                       } else {
                           console.warn("Aucun intervenant trouvé ou réponse invalide :", response.message || response.error);
                       }
                   },
                   error: function (xhr, status, error) {
                       console.log("Erreur AJAX (Intervenants) :");
                       console.error(error);
                   }
               });

            let circonstance_id = $('#circonstance_id').val();

            $("#modal-sinistre_garantie #table_add_sinistre_garantie tbody").empty();
            $('#garantie-message-warning').hide();

            if (circonstance_id) {
                $("#form_update_sinistre_gestionnaire #btn_ajout_garantie").show();

                function renderGarantiesTable(data) {
                    const tbody = $("#table_garantie_sinistre tbody");
                    tbody.empty();

                    data.forEach((row, index) => {
                        let clotureButton = '';
                        let deleteButton = `
                            <button class="btn btn-danger btn-sm btn-delete-garantie" type="button">
                                <i class="fa fa-trash-o"></i>
                            </button>
                        `;

                        // Afficher le bouton btn-cloture-garantie uniquement si row.sinistre_id existe
                        if (row.sinistre_id) {
                            let montant = parseFloat(String(row.montant).replace(/\s/g, '').replace(',', '.')) || 0;

                            if (montant !== 0) {
                                clotureButton = `
                                    <button class="btn btn-info btn-sm btn-cloture-garantie" type="button" disabled>
                                        <i class="fas fa-archive"></i>
                                    </button>
                                `;
                            }else{
                                clotureButton = `
                                    <button class="btn btn-info btn-sm btn-cloture-garantie" type="button">
                                        <i class="fas fa-archive"></i>
                                    </button>
                                `;
                            }
                            // Ne pas afficher le bouton delete si sinistre_id existe
                            deleteButton = '';
                        }

                        tbody.append(`
                            <tr data-id="${row.id}" data-garantie_id="${row.garantie_id}">
                                <td>
                                    ${clotureButton}
                                    ${deleteButton}
                                </td>
                                <td>${row.nom || ''}</td>
                                <td>${row.franchise || ''}</td>
                                <td>${row.capital || ''}</td>
                                <td>${row.mouvement || ''}</td>
                                <td>${row.date_ajout || ''}</td>
                            </tr>
                        `);
                    });
                }

                // Requête initiale pour récupérer les garanties
                $.ajax({
                    url: "/sinistre/recuperer_garantie_sinistre/",
                    type: "GET",
                    data: {
                        sinistre_id: selectedSinistreId
                    },
                    success: function (response) {
                        if (response.success && Array.isArray(response.data)) {
                            renderGarantiesTable(response.data);
                        } else {
                            console.warn("Aucune garantie trouvé ou réponse invalide :", response.message || response.error);
                        }
                    },
                    error: function (xhr, status, error) {
                        console.log("Erreur AJAX (Garanties)");
                        console.error(error);
                    }
                });

                // Requête AJAX pour récupérer les garanties par circonstance
                $.ajax({
                    url: "/sinistre/get_garanties_by_circonstance/",
                    type: "GET",
                    data: { circonstance_id: circonstance_id },
                    success: function (data) {
                        if (data && data.garanties && data.garanties.length > 0) {
                            data.garanties.forEach((garantie, index) => {
                                let row = `
                                    <tr>
                                        <td style="vertical-align:middle;">
                                            <input type="checkbox" class="form-control garantie-checkbox" name="garantie_${garantie.id}" value="${garantie.id}" style="width: 1rem; height: 1.25rem;">
                                        </td>
                                        <td style="vertical-align:middle;">${garantie.nom}</td>
                                        <td style="vertical-align:middle;padding:5px;">
                                            <input type="text" class="form-control form-control-sm franchise-input" name="franchise_${garantie.id}" value="" onkeypress="isInputNumber(event)" oninput="formatMontant(this)" disabled>
                                        </td>
                                        <td style="vertical-align:middle;padding:5px;">
                                            <input type="text" class="form-control form-control-sm capital-input" name="capital_${garantie.id}" value="" onkeypress="isInputNumber(event)" oninput="formatMontant(this)" disabled>
                                        </td>
                                    </tr>
                                `;
                                $("#modal-sinistre_garantie #table_add_sinistre_garantie tbody").append(row);
                            });
                        } else {
                            $('#garantie-message-warning').text('Aucune garantie trouvée pour cette circonstance.').show();
                        }
                    },
                    error: function (xhr, status, error) {
                        const errorMessage = 'Erreur lors de la récupération des garanties. Veuillez réessayer.';
                        try {
                            const errorResponse = JSON.parse(xhr.responseText);
                            $('#garantie-message-error').text(errorResponse.error || errorMessage).show();
                        } catch (e) {
                            $('#garantie-message-error').text(errorMessage).show();
                        }
                        setTimeout(() => $('#garantie-message-error').fadeOut(5000), 500);
                    },
                });

                $('#btn_save_sinistre_garantie').on('click', function () {
                    const garanties = [];

                    $('#table_add_sinistre_garantie tbody tr').each(function () {
                        const checkbox = $(this).find('.garantie-checkbox');
                        if (checkbox.is(':checked')) {
                            const garantieId = checkbox.val();
                            const nom = $(this).find('td:nth-child(2)').text().trim();
                            const franchise = $(this).find('.franchise-input').val();
                            const capital = $(this).find('.capital-input').val();

                            garanties.push({
                                id: garantieId,
                                nom: nom,
                                franchise: franchise,
                                capital: capital
                            });
                        }
                    });

                    if (garanties.length === 0) {
                        $("#garantie-modal-warning").text("Veuillez cocher au moins une garantie.").show().delay(5000).fadeOut();
                        return;
                    }

                    // Requête POST pour ajouter des garanties
                    $.ajax({
                        url: '/sinistre/ajout-garantie-sinistre/',
                        type: 'POST',
                        data: JSON.stringify({ garanties: garanties }),
                        contentType: 'application/json',
                        success: function (response) {
                            if (response.success) {
                                $("#garantie-modal-success").text(response.message).show().delay(5000).fadeOut();

                                // Utiliser la fonction renderGarantiesTable pour afficher les données
                                renderGarantiesTable(response.data);

                                $("#form_add_sinistre_garantie").trigger("reset");
                            } else {
                                $("#garantie-modal-warning").text(response.message).show().delay(5000).fadeOut();
                            }
                        },
                        error: function (xhr) {
                            const response = xhr.responseJSON;
                            const message = response?.message || "Une erreur est survenue. Veuillez réessayer.";
                            const target = xhr.status === 400 ? "#garantie-modal-warning" : "#garantie-modal-error";
                            $(target).text(message).show().delay(5000).fadeOut();
                        }
                    });

                });

                // Suppression de garantie sinistre
                $(document).on('click', '.btn-delete-garantie', function () {
                    const row = $(this).closest('tr');
                    const id = row.data('id');

                    $.ajax({
                        url: `/sinistre/supprimer_garantie/${id}/`,
                        type: 'POST',
                        headers: { 'X-CSRFToken': getCookie('csrftoken') },
                        success: function (response) {
                            if (response.success) {
                                row.remove();
                            } else {
                                console.error(response.error || 'Erreur lors de la suppression.');
                            }
                        },
                        error: function () {
                            notifyWarning("Erreur de communication avec le serveur.");
                            return;
                        }
                    });
                });

                // Clôture de garantie sinistre
                $(document).on('click', '.btn-cloture-garantie', function () {
                    const row = $(this).closest('tr');
                    const garantie_id = row.data('garantie_id');

                    let n = noty({
                        text: 'Voulez-vous vraiment clôturer cette garantie ?',
                        type: 'warning',
                        dismissQueue: true,
                        layout: 'center',
                        theme: 'defaultTheme',
                        buttons: [
                            {
                                addClass: 'btn btn-primary',
                                text: 'OUI',
                                onClick: function ($noty) {
                                    $noty.close();

                                    // Confirmation obtenue, envoyer la requête AJAX
                                    $.ajax({
                                        url: `/sinistre/cloture_garantie/${garantie_id}/`,
                                        type: 'POST',
                                        headers: { 'X-CSRFToken': getCookie('csrftoken') },
                                        success: function (response) {
                                            if (response.success) {
                                                row.find('td').eq(4).text('Cloture'); // Mettre à jour la colonne mouvement
                                                notifySuccess('La garantie a été clôturée avec succès.');
                                            } else {
                                                console.error(response.error || 'Erreur lors de la clôture.');
                                                notifyWarning('Échec de la clôture de la garantie.');
                                            }
                                        },
                                        error: function () {
                                            console.error('Erreur de communication avec le serveur.');
                                            notifyWarning('Erreur lors de la communication avec le serveur.');
                                        }
                                    });
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

                }
            else {
                $("#form_update_sinistre_gestionnaire #btn_ajout_garantie").hide();
            }
         }
    }

    manage_sinistre_change();

    $(document).on('change', "#form_update_sinistre_gestionnaire #sinistre_id", function () {

         manage_sinistre_change();

    });

    // ----------- UTILITAIRES -----------

    // Convertit une chaîne en nombre
    function parseNumber(str) {
        if (!str) return 0;
        return parseFloat(str.replace(/\s/g, '').replace(',', '.')) || 0;
    }

    // Formate un nombre avec séparateurs FR et signe
    function formatValue(value) {
        const absVal = Math.abs(value);
        let formatted = absVal.toLocaleString('fr-FR');
        return value < 0 ? `-${formatted}` : formatted;
    }

    // Formate et met à jour l'input
    function formatMontant(input) {
        let value = parseNumber(input.value);
        input.value = formatValue(value);
        return value;
    }

    // Vérifie si la ligne est un poste négatif
    function isNegativePoste(ligne) {
        const cell = ligne.find('td[data-sens]');
        return cell.length && cell.data('sens').toLowerCase().includes('negatif');
    }

    function calculerTotauxParGarantie() {
        $('.garantie-header').each(function () {
            const garantieId = $(this).data('garantie-id');
            let totalEstimation = 0, totalRegle = 0;

            $('#table_provision_sinistre tbody tr:not(:last-child)').each(function () {
                const ligne = $(this);
                if (!ligne.find('td[data-sens]').length) return;

                const negatif = isNegativePoste(ligne);

                const estimation = parseNumber(
                    ligne.find(`input[id^="montant_provision_"][id$="_${garantieId}"]`).val()
                );
                const regle = parseNumber(
                    ligne.find(`input[id^="montant_regle_"][id$="_${garantieId}"]`).val()
                );

                let valEstimation = estimation;
                let valRegle = regle;

                if (negatif) {
                    valEstimation = -Math.abs(estimation);
                    valRegle = -Math.abs(regle);
                }

                const provision = valEstimation - valRegle;
                ligne.find(`input[id^="provisionne_"][id$="_${garantieId}"]`).val(formatValue(provision));

                totalEstimation += valEstimation;
                totalRegle += valRegle;
            });

            const totalProvisionne = totalEstimation - totalRegle;

            $(`#total_montant_provision_${garantieId}`).val(formatValue(totalEstimation));
            $(`#total_montant_regle_${garantieId}`).val(formatValue(totalRegle));
            $(`#total_provisionne_${garantieId}`).val(formatValue(totalProvisionne));
        });
    }

    function validerRegle(input, ligne, valeur) {
        const garantieId = input.attr('id').split('_').pop();
        const estimation = parseNumber(
            ligne.find(`input[id^="montant_provision_"][id$="_${garantieId}"]`).val()
        );

        if (valeur > estimation) {
            input.val('0').addClass('is-invalid');
            return false;
        } else {
            input.removeClass('is-invalid');
            return true;
        }
    }

    $('.calculs_montant_garantie_sinistre')
    .on('input', function () {
        // Prevent formatting on readonly fields
        if ($(this).prop('readonly')) {
            return;
        }
        formatMontant(this);
        calculerTotauxParGarantie();
    })
    .on('blur', function () {
        const input = $(this);
        // Only proceed if the field is not readonly
        if (input.prop('readonly')) {
            return;
        }

        const ligne = input.closest('tr');
        let valeur = formatMontant(this); // récupère la valeur numérique

        // Validation du champ "Déjà réglé"
        if (input.data('type') === 'montant_regle' && !isNegativePoste(ligne)) {
            if (!validerRegle(input, ligne, valeur)) return;
        }

        // Franchise → toujours négatif
        if (isNegativePoste(ligne) && valeur > 0) {
            valeur = -valeur;
            input.val(formatValue(valeur));
        }

        calculerTotauxParGarantie();
    });

    calculerTotauxParGarantie();


    function calculerTotauxGarantieRecours() {
        $('.garantie-header').each(function () {
            const garantieId = $(this).data('garantie-id');
            let totalEstimation = 0, totalRegleRecours = 0;

            $('#table_recours_sinistre tbody tr:not(:last-child)').each(function () {
                const ligne = $(this);
                if (!ligne.find('td[data-sens]').length) return;

                const negatif = isNegativePoste(ligne);

                const estimation = parseNumber(
                    ligne.find(`input[id^="montant_recours_"][id$="_${garantieId}"]`).val()
                );
                const regle = parseNumber(
                    ligne.find(`input[id^="montant_regle_recours_"][id$="_${garantieId}"]`).val()
                );

                let valEstimation = estimation;
                let valRegle = regle;

                if (negatif) {
                    valEstimation = -Math.abs(estimation);
                    valRegle = -Math.abs(regle);
                }

                const recours = valEstimation - valRegle;
                ligne.find(`input[id^="recours_"][id$="_${garantieId}"]`).val(formatValue(recours));

                totalEstimation += valEstimation;
                totalRegleRecours += valRegle;
            });

            const totalRecours = totalEstimation - totalRegleRecours;

            $(`#total_montant_recours_${garantieId}`).val(formatValue(totalEstimation));
            $(`#total_montant_regle_recours_${garantieId}`).val(formatValue(totalRegleRecours));
            $(`#total_recours_${garantieId}`).val(formatValue(totalRecours));
        });
    }

    function validerRegle(input, ligne, valeur) {
        const garantieId = input.attr('id').split('_').pop();
        const estimation = parseNumber(
            ligne.find(`input[id^="montant_recours_"][id$="_${garantieId}"]`).val()
        );

        if (valeur > estimation) {
            input.val('0').addClass('is-invalid');
            return false;
        } else {
            input.removeClass('is-invalid');
            return true;
        }
    }

    $('.calculs_montant_recours_garantie_sinistre')
        .on('input', function () {
            formatMontant(this);
            calculerTotauxGarantieRecours();
        })
        .on('keypress', function (evt) {
            const charCode = evt.which || evt.keyCode;
            if (charCode > 31 && (charCode < 48 || charCode > 57) && charCode !== 45) {
                evt.preventDefault(); // Autorise seulement chiffres et "-"
            }
        })
        .on('blur', function () {
            const input = $(this);
            const ligne = input.closest('tr');
            let valeur = formatMontant(this); // récupère la valeur numérique

            // Validation du champ "Déjà réglé"
            if (input.data('type') === 'montant_regle_recours' && !isNegativePoste(ligne)) {
                if (!validerRegle(input, ligne, valeur)) return;
            }

            // Franchise → toujours négatif
            if (isNegativePoste(ligne) && valeur > 0) {
                valeur = -valeur;
                input.val(formatValue(valeur));
            }

            calculerTotauxGarantieRecours();
        });

    calculerTotauxGarantieRecours();

    function calculerTotauxReglementSinistre() {
        $('.garantie-header').each(function () {
            const garantieId = $(this).data('garantie-id');
            let totalReglement = 0;

            $('#table_montant_reglements_sinistre tbody tr:not(:last-child)').each(function () {
                const ligne = $(this);
                if (!ligne.find('td[data-sens]').length) return;

                const negatif = isNegativePoste(ligne);
                const montant = parseNumber(
                    ligne.find(`input[id^="montant_reglement_"][id$="_${garantieId}"]`).val()
                );

                let val = negatif ? -Math.abs(montant) : montant;
                totalReglement += val;
            });

            $(`#total_montant_reglement_sinistre${garantieId}`).val(formatValue(totalReglement));
        });

        // Calcul du total général
        let totalGeneral = 0;
        $('input.total_montant_reglement_sinistre').each(function () {
            totalGeneral += parseNumber($(this).val());
        });
        $('#total_a_regler_sinistre').val(formatValue(totalGeneral));
    }

    //Vérifie que la valeur saisie respecte la provision
    function verifierProvision(input) {
        const idParts = input.attr('id').split('_');
        const posteId = idParts[2];     // ex: montant_reglement_5_3  → 5 = poste
        const garantieId = idParts[3];  // → 3 = garantie

        const provisionInput = $(`#montant_recours_encaissement_${posteId}_${garantieId}`);
        const provision = parseNumber(provisionInput.val());
        const valeur = parseNumber(input.val());

        if (provision <= 0) {
            notifyError("Le poste dommage de la garantie n'est pas provisionné !");
            input.val("");
            return false;
        }

        if (valeur > provision) {
            notifyWarning("Le montant saisi dépasse la provision !");
            input.val("").addClass("is-invalid");
            return false;
        }

        input.removeClass("is-invalid");
        return true;
    }

    $('.calculs_montant_reglement_sinistre')
        .on('input', function () {
            formatMontant(this);
            verifierProvision($(this));
            calculerTotauxReglementSinistre();
        })
        .on('keypress', function (evt) {
            const charCode = evt.which || evt.keyCode;
            if (charCode > 31 && (charCode < 48 || charCode > 57) && charCode !== 45) {
                evt.preventDefault(); // Autorise seulement chiffres et "-"
            }
        })
        .on('blur', function () {
            const input = $(this);
            const ligne = input.closest('tr');
            let valeur = formatMontant(this);

            // Franchise → toujours négatif
            if (isNegativePoste(ligne) && valeur > 0) {
                valeur = -valeur;
                input.val(formatValue(valeur));
            }

            verifierProvision(input);
            calculerTotauxReglementSinistre();
        });

    calculerTotauxReglementSinistre();

    function calculerTotauxEncaissementRecoursSinistre() {
        $('.garantie-header').each(function () {
            const garantieId = $(this).data('garantie-id');
            let totalRecours = 0;

            $('#table_montant_encaissement_recours_sinistre tbody tr:not(:last-child)').each(function () {
                const ligne = $(this);
                if (!ligne.find('td[data-sens]').length) return;

                const negatif = isNegativePoste(ligne);
                const montantInput = ligne.find(`input[id^="montant_encaissement_recour_"][id$="_${garantieId}"]`);
                const montant = parseNumber(montantInput.val());

                let val = negatif ? -Math.abs(montant) : montant;
                totalRecours += val;
            });

            $(`#total_montant_encaissement_recour_${garantieId}`).val(formatValue(totalRecours));
        });

        let totalGeneral = 0;
        $('input.total_montant_encaissement_recour').each(function () {
            totalGeneral += parseNumber($(this).val());
        });
        $('#total_a_encaisser_sinistre').val(formatValue(totalGeneral));
    }

    function verifierRecours(input) {
        const idParts = input.attr('id').split('_');
        const posteId = idParts[3];
        const garantieId = idParts[4];

        const recoursInput = $(`#montant_recours_encaissement_${posteId}_${garantieId}`);
        const recours = parseNumber(recoursInput.val());
        const valeur = parseNumber(input.val());

        if (recours <= 0) {
            notifyError("Le poste dommage de la garantie n'est pas provisionné pour le recours !");
            input.val("");
            return false;
        }

        if (valeur > recours) {
            notifyWarning("Le montant saisi dépasse le recours !");
            input.val("").addClass("is-invalid");
            return false;
        }

        input.removeClass("is-invalid");
        return true;
    }

    $('.calculs_montant_encaissement_recour')
        .on('input', function () {
            formatMontant(this);
            verifierRecours($(this));
            calculerTotauxEncaissementRecoursSinistre();
        })
        .on('keypress', function (evt) {
            const charCode = evt.which || evt.keyCode;
            if (charCode > 31 && (charCode < 48 || charCode > 57) && charCode !== 45) {
                evt.preventDefault();
            }
        })
        .on('blur', function () {
            const input = $(this);
            const ligne = input.closest('tr');
            let valeur = parseNumber(input.val());

            if (isNegativePoste(ligne) && valeur > 0) {
                valeur = -valeur;
                input.val(formatValue(valeur));
            }

            verifierRecours(input);
            calculerTotauxEncaissementRecoursSinistre();
        });

    calculerTotauxEncaissementRecoursSinistre();

});


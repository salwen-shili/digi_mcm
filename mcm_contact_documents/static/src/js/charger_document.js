odoo.define('mcm_contact_documents.charger_document', function (require) {
'use strict';

var publicWidget = require('web.public.widget');


publicWidget.registry.digimoov_documents = publicWidget.Widget.extend({
    selector: '#digimoov_my_documents_form1',
    events: {
        'click #domicile_personnel_oui': 'domicile_personnel',
        'click #domicile_personnel_non': 'domicile_personnel',
    },

        domicile_personnel: function (ev) {
        var self = this;
        var domicile_personnel_oui = document.getElementById('domicile_personnel_oui');
        var domicile_personnel_non = document.getElementById('domicile_personnel_non');
        var identite_hebergeur_recto = document.getElementById('identite_hebergeur_recto_form');
        var identite_hebergeur_verso = document.getElementById('identite_hebergeur_verso_form');
        var attestation_hebergement = document.getElementById('attestation_hebergement_form');
        var justificatif_domicile_oui = document.getElementById('justificatif_domicile_form_oui');
        var justificatif_domicile_non = document.getElementById('justificatif_domicile_form_non');
        var identite_hebergeur_recto_input = document.getElementById('identite_hebergeur_recto_id');
        var identite_hebergeur_verso_input = document.getElementById('identite_hebergeur_verso_id');
        var attestation_hebergement_input = document.getElementById('attestation_hebergement_id');
        var justificatif_domicile_input_oui = document.getElementById('justificatif_domicile_id_oui');
        var justificatif_domicile_input_non = document.getElementById('justificatif_domicile_id_non');


        if(domicile_personnel_oui.checked){
            domicile_personnel_non = false;
            if(identite_hebergeur_recto) {
                identite_hebergeur_recto.style.display='none';
                identite_hebergeur_recto.className='form-group row form-field';
                identite_hebergeur_recto_input.required = false;
            }
            if(identite_hebergeur_verso) {
                identite_hebergeur_verso.style.display='none';
                identite_hebergeur_verso.className='form-group row form-field';
                identite_hebergeur_verso_input.required = false;
            }
            if(attestation_hebergement) {
                attestation_hebergement.style.display='none';
                attestation_hebergement.className='form-group row form-field';
                attestation_hebergement_input.required = false;
            }
            if(justificatif_domicile_oui) {
                justificatif_domicile_oui.style.display='block';
                justificatif_domicile_oui.className='form-group row form-field o_website_form_required';
                justificatif_domicile_input_oui.required = true;
            }
            if(justificatif_domicile_non) {
                justificatif_domicile_non.style.display='none';
                justificatif_domicile_non.className='form-group row form-field';
                justificatif_domicile_input_non.required = false;
            }
        }
        else if(domicile_personnel_non.checked){
            domicile_personnel_oui.false;
            if(identite_hebergeur_recto) {
                identite_hebergeur_recto.style.display='block';
                identite_hebergeur_recto.className='form-group row form-field o_website_form_required';
                identite_hebergeur_recto_input.required = true;

            }
            if(identite_hebergeur_verso) {
                identite_hebergeur_verso.style.display='block';
                identite_hebergeur_verso.className='form-group row form-field o_website_form_required';
                identite_hebergeur_verso_input.required = true;

            }
            if(attestation_hebergement) {
                attestation_hebergement.style.display='block';
                attestation_hebergement.className='form-group row form-field o_website_form_required';
                attestation_hebergement_input.required = true;
            }
            if(justificatif_domicile_non) {
                justificatif_domicile_non.style.display='block';
                justificatif_domicile_non.className='form-group row form-field';
                justificatif_domicile_input_non.required = true;
            }
            if(justificatif_domicile_oui) {
                justificatif_domicile_oui.style.display='none';
                justificatif_domicile_oui.className='form-group row form-field o_website_form_required';
                justificatif_domicile_input_oui.required = false;
            }
        }


               },

})

publicWidget.registry.check_digimoov_files = publicWidget.Widget.extend({
    selector: '#digimoov_my_documents_form1',
    events: {
        'change input[type="file"]': '_onCheckType',
    },
        _onCheckType: function (ev)
        {

            var id_of_input=ev.target.id;
            var file=null;
            var type=null;
            var input_id=null;
            var check_type=false
            if (id_of_input)
            {

                 var file=document.getElementById(id_of_input).files[0];
                 var input_id=document.getElementById(id_of_input)


                 if (file != null)
                 {
                    var type=file['type'];
                    var types = ['image/png' , 'image/jpg' , 'image/jpeg' , 'image/bmp' , 'image/gif' , 'image/svg+xml' , 'application/pdf'];
                    if (types.includes(type)){
                        check_type=true;
                    }
                    if (type != null)
                    {
                     if (check_type==false)
                        {
                            input_id.value='';
                            alert('Formats possibles : jpg, jpeg, png, pdf');
                        }
                    }
                 }
            }
        },
})


});
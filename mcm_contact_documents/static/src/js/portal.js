odoo.define('mcm_contact_documents.portal', function (require) {
  'use strict';

  var publicWidget = require('web.public.widget');
  var website = $('html');

  if (window.location.href.includes('manual')) {
    if (website.attr('data-website-id') == 1) {
      console.log('js mcm');
      $('#identity').bind('change', function () {
        var filename = $('#identity').val();
        if (/^\s*$/.test(filename)) {
          $('#file-upload1').removeClass('active');
          $('#noFile1').text('No file chosen...');
        } else {
          $('#file-upload1').addClass('active');
          $('#noFile1').text(filename.replace('C:\\fakepath\\', ''));
        }
      });
      $('#identity2').bind('change', function () {
        var filename = $('#identity2').val();
        if (/^\s*$/.test(filename)) {
          $('#file-upload2').removeClass('active');
          $('#noFile2').text('No file chosen...');
        } else {
          $('#file-upload2').addClass('active');
          $('#noFile2').text(filename.replace('C:\\fakepath\\', ''));
        }
      });
      $('#permis').bind('change', function () {
        var filename = $('#permis').val();
        if (/^\s*$/.test(filename)) {
          $('#file-upload3').removeClass('active');
          $('#noFile3').text('No file chosen...');
        } else {
          $('#file-upload3').addClass('active');
          $('#noFile3').text(filename.replace('C:\\fakepath\\', ''));
        }
      });

      $('#permis1').bind('change', function () {
        var filename = $('#permis1').val();
        if (/^\s*$/.test(filename)) {
          $('#file-upload4').removeClass('active');
          $('#noFile4').text('No file chosen...');
        } else {
          $('#file-upload4').addClass('active');
          $('#noFile4').text(filename.replace('C:\\fakepath\\', ''));
        }
      });
    }
    if (website.attr('data-website-id') == 2) {
      $('#identity').bind('change', function () {
        var filename = $('#identity').val();
        if (/^\s*$/.test(filename)) {
          $('#file-upload1').removeClass('active');
          $('#noFile1').text('No file chosen...');
        } else {
          $('#file-upload1').addClass('active');
          $('#noFile1').text(filename.replace('C:\\fakepath\\', ''));
        }
      });
      $('#identity2').bind('change', function () {
        var filename = $('#identity2').val();
        if (/^\s*$/.test(filename)) {
          $('#file-upload2').removeClass('active');
          $('#noFile2').text('No file chosen...');
        } else {
          $('#file-upload2').addClass('active');
          $('#noFile2').text(filename.replace('C:\\fakepath\\', ''));
        }
      });
      // $("#permis").bind("change", function () {
      //   var filename = $("#permis").val();
      //   if (/^\s*$/.test(filename)) {
      //     $("#file-upload3").removeClass("active");
      //     $("#noFile3").text("No file chosen...");
      //   } else {
      //     $("#file-upload3").addClass("active");
      //     $("#noFile3").text(filename.replace("C:\\fakepath\\", ""));
      //   }
      // });

      // $("#permis1").bind("change", function () {
      //   var filename = $("#permis1").val();
      //   if (/^\s*$/.test(filename)) {
      //     $("#file-upload4").removeClass("active");
      //     $("#noFile4").text("No file chosen...");
      //   } else {
      //     $("#file-upload4").addClass("active");
      //     $("#noFile4").text(filename.replace("C:\\fakepath\\", ""));
      //   }
      // });

      $('#mcm_my_documents_form').submit(function (event) {
        event.preventDefault();
        window.location.href = '#popup1';
      });
      function onClickBtn() {
        window.location.href = '#';

        $('#mcm_my_documents_form').submit();
        $('div.spanner').addClass('show');
        $('div.overlay').addClass('show');
      }
    }
  }

  publicWidget.registry.digi_documents = publicWidget.Widget.extend({
    selector: '#digimoov_my_documents_form',
    events: {
      'click #check_domicile_not_checked': 'check_domicile',
      'click #check_domicile_checked': 'check_domicile',
      'change #cerfa': 'verify_cerfa',
      'change input[type="file"]': '_onCheckType',
    },

    check_domicile: function (ev) {
      var self = this;
      var domic_checked = document.getElementById('check_domicile_checked');
      var domic_not_checked = document.getElementById(
        'check_domicile_not_checked'
      );
      var domic_identity_hebergeur = document.getElementById(
        'o_website_form_identity_hebergeur'
      );
      var domic_identity_hebergeur1 = document.getElementById(
        'o_website_form_identity_hebergeur1'
      );
      var domic_attestation_hebergeur = document.getElementById(
        'o_website_form_attestation_hebergeur'
      );
      var identity_hebergeur = document.getElementById('identity_hebergeur');
      var identity_hebergeur1 = document.getElementById('identity_hebergeur1');
      var attestation_hebergeur = document.getElementById(
        'attestation_hebergeur'
      );
      if (domic_checked.checked) {
        if (domic_identity_hebergeur) {
          domic_identity_hebergeur.style.display = 'none';
          domic_identity_hebergeur.className = 'form-group row form-field';
          identity_hebergeur.required = 0;
        }
        if (domic_identity_hebergeur1) {
          domic_identity_hebergeur1.style.display = 'none';
          domic_identity_hebergeur1.className = 'form-group row form-field';
          identity_hebergeur1.required = 0;
        }
        if (domic_identity_hebergeur1) {
          domic_identity_hebergeur1.style.display = 'none';
          domic_identity_hebergeur1.className = 'form-group row form-field';
          identity_hebergeur1.required = 0;
        }
        if (domic_attestation_hebergeur) {
          domic_attestation_hebergeur.style.display = 'none';
          domic_attestation_hebergeur.className = 'form-group row form-field';
          attestation_hebergeur.required = 0;
        }
      }
      if (domic_not_checked.checked) {
        if (domic_identity_hebergeur) {
          domic_identity_hebergeur.style.display = 'block';
          domic_identity_hebergeur.className =
            'form-group row form-field o_website_form_required';
          identity_hebergeur.required = 1;
        }
        if (domic_identity_hebergeur1) {
          domic_identity_hebergeur1.style.display = 'block';
          domic_identity_hebergeur1.className =
            'form-group row form-field o_website_form_required';
          identity_hebergeur1.required = 1;
        }
        if (domic_identity_hebergeur1) {
          domic_identity_hebergeur1.style.display = 'block';
          domic_identity_hebergeur1.className =
            'form-group row form-field o_website_form_required';
          identity_hebergeur1.required = 1;
        }
        if (domic_attestation_hebergeur) {
          domic_attestation_hebergeur.style.display = 'block';
          domic_attestation_hebergeur.className =
            'form-group row form-field o_website_form_required';
          attestation_hebergeur.required = 1;
        }
      }
    },
    verify_cerfa: function (ev) {
      var cerfa_lenth_files = document.getElementById('cerfa').files.length;
      var div_cerfa_2 = document.getElementById('o_website_form_cerfa_2');
      var div_cerfa_3 = document.getElementById('o_website_form_cerfa_3');
      var cerfa_2 = document.getElementById('cerfa2');
      var cerfa_3 = document.getElementById('cerfa3');
      var label_cerfa = document.getElementById('label_cerfa_3_pages');
      if (cerfa_lenth_files == 1) {
        var file = document.getElementById('cerfa').files[0];
        var type = file['type'];
        if (type.includes('image/')) {
          div_cerfa_2.style.display = 'block';
          div_cerfa_2.className =
            'form-group row form-field o_website_form_required';
          cerfa_2.required = 1;
          div_cerfa_3.style.display = 'block';
          div_cerfa_3.className =
            'form-group row form-field o_website_form_required';
          cerfa_3.required = 1;
          $('#label_cerfa_3_pages').text('CERFA 11414-05 Page 1');
        } else {
          div_cerfa_2.style.display = 'none';
          div_cerfa_2.className = 'form-group row form-field';
          cerfa_2.required = 0;
          div_cerfa_3.style.display = 'none';
          div_cerfa_3.className = 'form-group row form-field';
          cerfa_3.required = 0;
          $('#label_cerfa_3_pages').text('CERFA 11414-05 (Page1,2,3)');
        }
      } else if (cerfa_lenth_files > 1) {
        div_cerfa_2.style.display = 'none';
        div_cerfa_2.className = 'form-group row form-field';
        cerfa_2.required = 0;
        div_cerfa_3.style.display = 'none';
        div_cerfa_3.className = 'form-group row form-field';
        cerfa_3.required = 0;
        $('#label_cerfa_3_pages').text('CERFA 11414-05 (Page1,2,3)');
      }
    },
    _onCheckType: function (ev) {
      var id_of_input = ev.target.id;
      var file = null;
      var type = null;
      var input_id = null;
      var check_type = false;
      if (id_of_input) {
        var file = document.getElementById(id_of_input).files[0];
        var input_id = document.getElementById(id_of_input);

        if (file != null) {
          var type = file['type'];
          var types = [
            'image/png',
            'image/jpg',
            'image/jpeg',
            'image/bmp',
            'image/svg+xml',
            'application/pdf',
          ];
          if (types.includes(type)) {
            check_type = true;
          }
          if (type != null) {
            if (check_type == false) {
              input_id.value = '';
              alert('Formats possibles : jpg , png, pdf');
            }
          }
        }
      }
    },
  });
  publicWidget.registry.updated_documents = publicWidget.Widget.extend({
    selector: '#digimoov_updated_document_form',
    events: {
      'change #updated_document_cerfa': 'verify_cerfa',
    },

    verify_cerfa: function (ev) {
      var cerfa_lenth_files = document.getElementById('updated_document_cerfa')
        .files.length;
      var div_cerfa_2 = document.getElementById(
        'o_website_form_updated_cerfa_2'
      );
      var div_cerfa_3 = document.getElementById(
        'o_website_form_updated_cerfa_3'
      );
      var cerfa_2 = document.getElementById('updated_document_cerfa2');
      var cerfa_3 = document.getElementById('updated_document_cerfa2');
      var label_cerfa = document.getElementById('label_updated_document_cerfa');
      if (cerfa_lenth_files == 1) {
        var file = document.getElementById('updated_document_cerfa').files[0];
        var type = file['type'];
        if (type.includes('image/')) {
          div_cerfa_2.style.display = 'flex';
          div_cerfa_2.className =
            'form-group row form-field o_website_form_required';
          div_cerfa_3.style.display = 'flex';
          div_cerfa_3.className =
            'form-group row form-field o_website_form_required';
          $('#label_updated_document_cerfa').text('CERFA 11414-05 Page 1');
        } else {
          div_cerfa_2.style.display = 'none';
          div_cerfa_2.className = 'form-group row form-field';
          div_cerfa_3.style.display = 'none';
          div_cerfa_3.className = 'form-group row form-field';
          $('#label_updated_document_cerfa').text('CERFA 11414-05 (Page1,2,3)');
        }
      } else if (cerfa_lenth_files > 1) {
        div_cerfa_2.style.display = 'none';
        div_cerfa_2.className = 'form-group row form-field';
        cerfa_2.required = 0;
        div_cerfa_3.style.display = 'none';
        div_cerfa_3.className = 'form-group row form-field';
        cerfa_3.required = 0;
        $('#label_updated_document_cerfa').text('CERFA 11414-05 (Page1,2,3)');
      }
    },
  });

  publicWidget.registry.mcm_documents = publicWidget.Widget.extend({
    selector: '#mcm_my_documents_form',
    events: {
      'change input[type="file"]': '_onCheckType',
    },
    _onCheckType: function (ev) {
      var id_of_input = ev.target.id;
      var file = null;
      var type = null;
      var input_id = null;
      var check_type = false;
      if (id_of_input) {
        var file = document.getElementById(id_of_input).files[0];
        var input_id = document.getElementById(id_of_input);
        if (file != null) {
          var type = file['type'];
          var types = [
            'image/png',
            'image/jpg',
            'image/png',
            'image/jpg',
            'image/jpeg',
            'image/bmp',
            'application/pdf',
          ];
          if (types.includes(type)) {
            check_type = true;
          }
          if (type != null) {
            if (check_type == false) {
              input_id.value = '';
              alert('Formats possibles : jpg , png, pdf');
            }
          }
        }
      }
    },
  });
});

odoo.define('mcm_session_list_intervenants.portal', function (require) {
'use strict';
var publicWidget = require('web.public.widget');

    publicWidget.registry.digi_intervenent = publicWidget.Widget.extend({
    selector: '#digimoov_my_documents_form',
    events: {
    "click. intervenant_curriculum_vitae": "_onCheckType",
},


        _onCheckType: function (ev)
        {
            var id_of_input=ev.target.id;
            var curriculum_viatae =null;
            var type=null;
            var input_id=null;
            var check_type=false
            console.log('test123')
            if (id_of_input)
            {
                 var curriculum_viatae=document.getElementById(id_of_input).files[0];
                 var input_id=document.getElementById(id_of_input)

                 if (curriculum_viatae != null)
                 {
                    var type=curriculum_viatae['type'];
                    var types = ['image/png' , 'image/jpg' , 'image/jpeg' , 'application/pdf'];
                    if (types.includes(type)){
                        check_type=true;
                    }
                    if (type != null)
                    {
                     if (check_type==false)
                        {
                            input_id.value='';
                            alert('Formats possibles : jpg , png, pdf');
                        }
                    }
                 }
            }
        }
});

//publicWidget.registry.mcm_documents = publicWidget.Widget.extend({
//    selector: '#mcm_my_documents_form',
//    events: {
//        'change input[type="file"]': '_onCheckType',
//    },
//        _onCheckType: function (ev)
//        {
//            var id_of_input=ev.target.id;
//            var file=null;
//            var type=null;
//            var input_id=null;
//            var check_type=false
//            if (id_of_input)
//            {
//                 var file=document.getElementById(id_of_input).files[0];
//                 var input_id=document.getElementById(id_of_input)
//                 if (file != null)
//                 {
//                    var type=file['type'];
//                    var types = ['image/png' , 'image/jpg', 'application/pdf'];
//                    if (types.includes(type)){
//                        check_type=true;
//                    }
//                    if (type != null)
//                    {
//                     if (check_type==false)
//                        {
//                            input_id.value='';
//                            alert('Formats possibles : jpg , png, pdf');
//                        }
//                    }
//                 }
//            }
//        }
//})

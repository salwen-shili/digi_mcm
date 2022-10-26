# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _, api, http
from odoo.exceptions import UserError
from werkzeug.urls import url_join
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, formataddr


class InheritSignRequest(models.Model):
    _inherit = "sign.request.item"

    def send_signature_accesses(self, subject=None, message=None):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for signer in self:
            if not signer.partner_id or not signer.partner_id.email:
                continue
            if not signer.create_uid.email:
                continue
            tpl = self.env.ref('sign.sign_template_mail_request')
            if signer.partner_id.lang:
                tpl = tpl.with_context(lang=signer.partner_id.lang)
            message = """
        <xpath expr="//table" position="replace">
            <table border="0" cellpadding="0" cellspacing="0" style="padding-top:16px;background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;">
                <tbody><tr>
                    <td align="center">
                        <table border="0" cellpadding="0" cellspacing="0" width="590" style="padding:24px;background-color: white; color: #454748; border-collapse:separate;">
                            <tbody>
                                <tr>
                                    <td align="center">
                                        <table border="0" cellpadding="0" cellspacing="0" width="590" style="padding:24px;background-color: white; color: #454748; border-collapse:separate;">
                                            <tbody>
                                                <tr>
                                                    <td align="center" style="min-width:590px;">
                                                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color:white;padding: 0; border-collapse:separate;">
                                                            <tbody><tr>
                                                                <td valign="middle" align="right">
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td colspan="2" style="text-align:center;">

                                                                </td>
                                                            </tr>
                                                        </tbody></table>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="min-width:590px;">
                                                        
        
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <meta name="x-apple-disable-message-reformatting">
            <meta name="apple-mobile-web-app-capable" content="yes">
            <meta name="apple-mobile-web-app-status-bar-style" content="black">
            <meta name="format-detection" content="telephone=no">
            <title></title>
            <style type="text/css">
                /* Resets */
                .ReadMsgBody { width: 100%; background-color: #ebebeb;}
                .ExternalClass {width: 100%; background-color: #ebebeb;}
                .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td,
                .ExternalClass div {line-height:100%;}
                a[x-apple-data-detectors]{
                color:inherit !important;
                text-decoration:none !important;
                font-size:inherit !important;
                font-family:inherit !important;
                font-weight:inherit !important;
                line-height:inherit !important;
                }
                body {-webkit-text-size-adjust:none; -ms-text-size-adjust:none;}
                body {margin:0; padding:0;}
                .yshortcuts a {border-bottom: none !important;}
                .rnb-del-min-width{ min-width: 0 !important; }
                /* Add new outlook css start */
                .templateContainer{
                max-width:590px !important;
                width:auto !important;
                }
                /* Add new outlook css end */
                /* Image width by default for 3 columns */
                img[class="rnb-col-3-img"] {
                max-width:170px;
                }
                /* Image width by default for 2 columns */
                img[class="rnb-col-2-img"] {
                max-width:264px;
                }
                /* Image width by default for 2 columns aside small size */
                img[class="rnb-col-2-img-side-xs"] {
                max-width:180px;
                }
                /* Image width by default for 2 columns aside big size */
                img[class="rnb-col-2-img-side-xl"] {
                max-width:350px;
                }
                /* Image width by default for 1 column */
                img[class="rnb-col-1-img"] {
                max-width:550px;
                }
                /* Image width by default for header */
                img[class="rnb-header-img"] {
                max-width:590px;
                }
                /* Ckeditor line-height spacing */
                .rnb-force-col p, ul, ol{margin:0px!important;}
                .rnb-del-min-width p, ul, ol{margin:0px!important;}
                /* tmpl-2 preview */
                .rnb-tmpl-width{ width:100%!important;}
                /* tmpl-11 preview */
                .rnb-social-width{padding-right:15px!important;}
                /* tmpl-11 preview */
                .rnb-social-align{float:right!important;}
                /* Ul Li outlook extra spacing fix */
                li{mso-margin-top-alt: 0; mso-margin-bottom-alt: 0;}
                /* Outlook fix */
                table {mso-table-lspace:0pt; mso-table-rspace:0pt;}
                /* Outlook fix */
                table, tr, td {border-collapse: collapse;}
                /* Outlook fix */
                p,a,li,blockquote {mso-line-height-rule:exactly;}
                /* Outlook fix */
                .msib-right-img { mso-padding-alt: 0 !important;}
                @media only screen and (min-width:590px){
                /* mac fix width */
                .templateContainer{width:590px !important;}
                }
                @media screen and (max-width: 360px){
                /* yahoo app fix width "tmpl-2 tmpl-10 tmpl-13" in android devices */
                .rnb-yahoo-width{ width:360px !important;}
                }
                @media screen and (max-width: 380px){
                /* fix width and font size "tmpl-4 tmpl-6" in mobile preview */
                .element-img-text{ font-size:24px !important;}
                .element-img-text2{ width:230px !important;}
                .content-img-text-tmpl-6{ font-size:24px !important;}
                .content-img-text2-tmpl-6{ width:220px !important;}
                }
                @media screen and (max-width: 480px) {
                td[class="rnb-container-padding"] {
                padding-left: 10px !important;
                padding-right: 10px !important;
                }
                /* force container nav to (horizontal) blocks */
                td.rnb-force-nav {
                display: inherit;
                }
                /* fix text alignment "tmpl-11" in mobile preview */
                .rnb-social-text-left {
                width: 100%;
                text-align: center;
                margin-bottom: 15px;
                }
                .rnb-social-text-right {
                width: 100%;
                text-align: center;
                }
                }
                @media only screen and (max-width: 600px) {

                .rnb-text-center {text-align:center !important;}
                /* force container columns to (horizontal) blocks */
                th.rnb-force-col {
                display: block;
                padding-right: 0 !important;
                padding-left: 0 !important;
                width:100%;
                }
                table.rnb-container {
                width: 100% !important;
                }
                table.rnb-btn-col-content {
                width: 100% !important;
                }
                table.rnb-col-3 {
                /* unset table align="left/right" */
                float: none !important;
                width: 100% !important;
                /* change left/right padding and margins to top/bottom ones */
                margin-bottom: 10px;
                padding-bottom: 10px;
                /*border-bottom: 1px solid #eee;*/
                }
                table.rnb-last-col-3 {
                /* unset table align="left/right" */
                float: none !important;
                width: 100% !important;
                }
                table.rnb-col-2 {
                /* unset table align="left/right" */
                float: none !important;
                width: 100% !important;
                /* change left/right padding and margins to top/bottom ones */
                margin-bottom: 10px;
                padding-bottom: 10px;
                /*border-bottom: 1px solid #eee;*/
                }
                table.rnb-col-2-noborder-onright {
                /* unset table align="left/right" */
                float: none !important;
                width: 100% !important;
                /* change left/right padding and margins to top/bottom ones */
                margin-bottom: 10px;
                padding-bottom: 10px;
                }
                table.rnb-col-2-noborder-onleft {
                /* unset table align="left/right" */
                float: none !important;
                width: 100% !important;
                /* change left/right padding and margins to top/bottom ones */
                margin-top: 10px;
                padding-top: 10px;
                }
                table.rnb-last-col-2 {
                /* unset table align="left/right" */
                float: none !important;
                width: 100% !important;
                }
                table.rnb-col-1 {
                /* unset table align="left/right" */
                float: none !important;
                width: 100% !important;
                }
                img.rnb-col-3-img {
                /**max-width:none !important;**/
                width:100% !important;
                }
                img.rnb-col-2-img {
                /**max-width:none !important;**/
                width:100% !important;
                }
                img.rnb-col-2-img-side-xs {
                /**max-width:none !important;**/
                width:100% !important;
                }
                img.rnb-col-2-img-side-xl {
                /**max-width:none !important;**/
                width:100% !important;
                }
                img.rnb-col-1-img {
                /**max-width:none !important;**/
                width:100% !important;
                }
                img.rnb-header-img {
                /**max-width:none !important;**/
                width:100% !important;
                margin:0 auto;
                }
                img.rnb-logo-img {
                /**max-width:none !important;**/
                width:100% !important;
                }
                td.rnb-mbl-float-none {
                float:inherit !important;
                }
                .img-block-center{text-align:center !important;}
                .logo-img-center
                {
                float:inherit !important;
                }
                /* tmpl-11 preview */
                .rnb-social-align{margin:0 auto !important; float:inherit !important;}
                /* tmpl-11 preview */
                .rnb-social-center{display:inline-block;}
                /* tmpl-11 preview */
                .social-text-spacing{margin-bottom:0px !important; padding-bottom:0px !important;}
                /* tmpl-11 preview */
                .social-text-spacing2{padding-top:15px !important;}
                /* UL bullet fixed in outlook */
                ul {mso-special-format:bullet;}
                }
            </style>
            <style type="text/css">table{border-spacing: 0;} table td {border-collapse: collapse;}
            </style>
        


        <table border="0" align="center" width="100%" cellpadding="0" cellspacing="0" class="main-template" bgcolor="#ffffff" style="background-color:rgb(255, 255, 255);">

            <tbody>
                <tr>
                    <td align="center" valign="top">
                        <table border="0" cellpadding="0" cellspacing="0" width="590" class="templateContainer" style="!important;width:590px;">
                            <tbody>
                                <tr>

                                    <td align="center" valign="top">

                                        <table class="rnb-del-min-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:590px;" name="Layout_7113" id="Layout_7113">
                                            <tbody>
                                                <tr>
                                                    <td class="rnb-del-min-width" valign="top" align="center" style="min-width:590px;">
                                                        <a href="#" name="Layout_7113"></a>
                                                        <table width="100%" cellpadding="0" border="0" height="30" cellspacing="0">
                                                            <tbody>
                                                                <tr>
                                                                    <td valign="top" height="30">
                                                                        <img style="display:block;max-height:30px; max-width:20px;" src="https://img.mailinblue.com/new_images/rnb/rnb_space.gif">
                                                                    </td>
                                                                </tr>
                                                            </tbody>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(114, 25, 224);border-radius: 0px;">

                                            <table width="100%" cellpadding="0" border="0" cellspacing="0" name="Layout_5" id="Layout_5">
                                                <tbody>
                                                    <tr>
                                                        <td align="center" valign="top">
                                                            <a href="#" name="Layout_5"></a>
                                                            <table border="0" width="100%" cellpadding="0" cellspacing="0" class="rnb-container" bgcolor="#7219e0" style="height:0px;background-color: rgb(114, 25, 224); border-radius: 0px; border-collapse: separate; padding-left: 20px; padding-right: 20px;">
                                                                <tbody>
                                                                    <tr>
                                                                        <td class="rnb-container-padding" style="font-size:px;font-family: ; color: ;">

                                                                            <table border="0" cellpadding="0" cellspacing="0" class="rnb-columns-container" align="center" style="margin:auto;">
                                                                                <tbody>
                                                                                    <tr>

                                                                                        <th class="rnb-force-col" align="center" style="text-align:center;font-weight: normal">

                                                                                            <table border="0" cellspacing="0" cellpadding="0" align="center" class="rnb-col-1">

                                                                                                <tbody>
                                                                                                    <tr>
                                                                                                        <td height="10"></td>
                                                                                                    </tr>

                                                                                                    <tr>
                                                                                                        <td style="font-family:'Arial',Helvetica,sans-serif;color:#999; text-align:center;">

                                                                                                            <span style="color:#999;">
                                                                                                                <font color="#ffffff">
                                                                                                                    <span style="font-size:30px;">
                                                                                                                        <b>
                                                                                                                            DIGIMOOV
                                                                                                                        </b>
                                                                                                                    </span>
                                                                                                                </font>
                                                                                                            </span>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                    <tr>
                                                                                                        <td height="10"></td>
                                                                                                    </tr>
                                                                                                </tbody>
                                                                                            </table>
                                                                                        </th>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>
                                                                        </td>
                                                                    </tr>

                                                                </tbody>
                                                            </table>

                                                        </td>
                                                    </tr>

                                                </tbody>
                                            </table>
                                        </div>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(255, 255, 255);">

                                            <table class="rnb-del-min-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:100%;-webkit-backface-visibility: hidden; line-height: 10px;" name="Layout_56" id="Layout_56">
                                                <tbody>
                                                    <tr>
                                                        <td class="rnb-del-min-width" valign="top" align="center" style="min-width:590px;">
                                                            <a href="#" name="Layout_56"></a>
                                                            <table width="100%" class="rnb-container" cellpadding="0" border="0" bgcolor="#ffffff" align="center" cellspacing="0" style="background-color:rgb(255, 255, 255);">
                                                                <tbody>
                                                                    <tr>
                                                                        <td valign="top" align="center">
                                                                            <table cellspacing="0" cellpadding="0" border="0">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <td>
                                                                                            <div style="border-radius:0px;width:331;max-width:331px !important;border-top:0px None #000;border-right:0px None #000;border-bottom:0px None #000;border-left:0px None #000;border-collapse: separate;border-radius: 0px;">
                                                                                                <div>
                                                                                                    <img ng-if="col.img.source != 'url'" border="0" hspace="0" vspace="0" width="331" class="rnb-header-img" style="display:block;float:left; border-radius: 0px; " src="https://img.mailinblue.com/2380179/images/rnb/original/5e0d25e5ead0d69e436aa22e.png">
                                                                                                </div>
                                                                                                <div style="clear:both;"></div>
                                                                                            </div>
                                                                                        </td>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>

                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(255, 255, 255);border-radius: 0px;">

                                            <table class="rnb-del-min-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:100%;" name="Layout_35">
                                                <tbody>
                                                    <tr>
                                                        <td class="rnb-del-min-width" align="center" valign="top">
                                                            <a href="#" name="Layout_35"></a>
                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="rnb-container" bgcolor="#ffffff" style="background-color:rgb(255, 255, 255);padding-left: 20px; padding-right: 20px; border-collapse: separate; border-radius: 0px; border-bottom: 0px none rgb(200, 200, 200);">

                                                                <tbody>
                                                                    <tr>
                                                                        <td height="6" style="font-size:1px;line-height:6px; mso-hide: all;">
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td valign="top" class="rnb-container-padding" align="left">

                                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="rnb-columns-container">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <th class="rnb-force-col" style="text-align:left;font-weight: normal; padding-right: 0px;" valign="top">

                                                                                            <table border="0" valign="top" cellspacing="0" cellpadding="0" width="100%" align="left" class="rnb-col-1">

                                                                                                <tbody>
                                                                                                    <tr>
                                                                                                        <td style="font-size:14px;font-family:Arial,Helvetica,sans-serif, sans-serif; color:#3c4858;">
                                                                                                            <div>

                                                                                                            </div>

                                                                                                            <div style="line-height:24px;text-align: left;">
                                                                                                                <span style="font-size:16px;">
                                                                                                                    Bonjour,
                                                                                                                </span>
                                                                                                                <br>
                                                                                                                <span style="font-size:16px;">
                                                                                                                </span>
                                                                                                            </div>

                                                                                                            <div style="line-height:24px;text-align: left;">

                                                                                                            </div>

                                                                                                            <div style="line-height:24px;text-align: left;">
                                                                                                                <span style="font-size:16px;">
                                                                                                                </span>
                                                                                                                <br>
                                                                                                                <span style="font-size:16px;">
                                                                                                                    Dans
                                                                                                                    le
                                                                                                                    cadre
                                                                                                                    du
                                                                                                                    passage
                                                                                                                    de
                                                                                                                    votre
                                                                                                                    examen
                                                                                                                    de
                                                                                                                    capacité
                                                                                                                    de
                                                                                                                    transport
                                                                                                                    léger
                                                                                                                    de
                                                                                                                    marchandises,
                                                                                                                    nous
                                                                                                                    vous
                                                                                                                    remercions
                                                                                                                    de
                                                                                                                    bien
                                                                                                                    vouloir
                                                                                                                    signer
                                                                                                                    votre
                                                                                                                    Cerfa
                                                                                                                    et
                                                                                                                    nous
                                                                                                                    faire
                                                                                                                    parvenir
                                                                                                                    un
                                                                                                                    justificatif
                                                                                                                    de
                                                                                                                    domicile <strong>
                                                                                                                    de
                                                                                                                    -
                                                                                                                    3
                                                                                                                    mois
                                                                                                                </strong> à
                                                                                                                    votre
                                                                                                                    nom
                                                                                                                    (sinon
                                                                                                                    accompagné
                                                                                                                    de
                                                                                                                    l'attestation
                                                                                                                    d'hébergement
                                                                                                                    +
                                                                                                                    CNI
                                                                                                                    de
                                                                                                                    l'hébergeur)
                                                                                                                    afin
                                                                                                                    de
                                                                                                                    compléter
                                                                                                                    votre
                                                                                                                    dossier.
                                                                                                                </span>
                                                                                                            </div>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                    <tr>
                                                                                                        <td style="font-size:14px;font-family:Arial,Helvetica,sans-serif, sans-serif; color:#3c4858;">
                                                                                                            <br>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                </tbody>
                                                                                            </table>

                                                                                        </th>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td height="0" style="font-size:1px;line-height:0px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(255, 255, 255);border-radius: 0px;">

                                            <table class="rnb-del-min-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:100%;" name="Layout_66">
                                                <tbody>
                                                    <tr>
                                                        <td class="rnb-del-min-width" align="center" valign="top">
                                                            <a href="#" name="Layout_66"></a>
                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="rnb-container" bgcolor="#ffffff" style="background-color:rgb(255, 255, 255);padding-left: 20px; padding-right: 20px; border-collapse: separate; border-radius: 0px; border-bottom: 0px none rgb(200, 200, 200);">

                                                                <tbody>
                                                                    <tr>
                                                                        <td height="15" style="font-size:1px;line-height:15px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td valign="top" class="rnb-container-padding" align="left">

                                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="rnb-columns-container">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <th class="rnb-force-col" style="text-align:left;font-weight: normal; padding-right: 0px;" valign="top">

                                                                                            <table border="0" valign="top" cellspacing="0" cellpadding="0" width="100%" align="left" class="rnb-col-1">

                                                                                                <tbody>
                                                                                                    <tr>
                                                                                                        <td style="font-size:14px;font-family:Arial,Helvetica,sans-serif, sans-serif; color:#3c4858;">
                                                                                                            <div>

                                                                                                            </div>

                                                                                                            <div style="line-height:24px;text-align: left;">
                                                                                                                <span style="font-size:16px;">
                                                                                                                    <strong>
                                                                                                                        PS
                                                                                                                    </strong>
                                                                                                                    :
                                                                                                                    Veuillez
                                                                                                                    nous
                                                                                                                    envoyer
                                                                                                                    seulement
                                                                                                                    l'un
                                                                                                                    des
                                                                                                                    documents
                                                                                                                    énumérés
                                                                                                                    ci-dessous
                                                                                                                    en
                                                                                                                    cliquant
                                                                                                                    sur
                                                                                                                    le
                                                                                                                    bouton
                                                                                                                    plus
                                                                                                                    bas
                                                                                                                    :
                                                                                                                </span>
                                                                                                            </div>

                                                                                                            <div style="line-height:20px;">
                                                                                                                <br>
                                                                                                                <span style="font-size:16px;">
                                                                                                                    <strong>
                                                                                                                        -
                                                                                                                        Une
                                                                                                                        quittance
                                                                                                                        de
                                                                                                                        loyer
                                                                                                                    </strong>
                                                                                                                    <br>
                                                                                                                    <strong>
                                                                                                                        -
                                                                                                                    </strong>
                                                                                                                    <strong>
                                                                                                                        Une
                                                                                                                        quittance
                                                                                                                        d'électricité
                                                                                                                    </strong>
                                                                                                                    <br>
                                                                                                                    <strong>
                                                                                                                        -
                                                                                                                    </strong>
                                                                                                                    <strong>
                                                                                                                        Une
                                                                                                                        quittance
                                                                                                                        d'opérateur
                                                                                                                        d'eau
                                                                                                                    </strong>
                                                                                                                    <br>
                                                                                                                    <strong>
                                                                                                                        -
                                                                                                                    </strong>
                                                                                                                    <strong>
                                                                                                                        Une
                                                                                                                        quittance
                                                                                                                        d'opérateur
                                                                                                                        de
                                                                                                                        gaz
                                                                                                                    </strong>
                                                                                                                    <br>
                                                                                                                    <strong>
                                                                                                                        -
                                                                                                                        Une
                                                                                                                        quittance
                                                                                                                        d'opérateur
                                                                                                                        de
                                                                                                                        box
                                                                                                                        internet
                                                                                                                    </strong>
                                                                                                                </span>
                                                                                                            </div>

                                                                                                            <div style="line-height:20px;">

                                                                                                            </div>

                                                                                                            <div style="line-height:20px;">
                                                                                                                <span style="color:#FF0000;">
                                                                                                                    <span style="font-size:16px;">
                                                                                                                        <strong>
                                                                                                                            <br>
                                                                                                                        </strong>
                                                                                                                        <strong>
                                                                                                                            Remarque
                                                                                                                            :
                                                                                                                            Les
                                                                                                                            factures
                                                                                                                            de
                                                                                                                            téléphone
                                                                                                                            mobile
                                                                                                                            et
                                                                                                                            les
                                                                                                                            avis
                                                                                                                            d'imposition
                                                                                                                            ne
                                                                                                                            sont
                                                                                                                            pas
                                                                                                                            acceptés.
                                                                                                                        </strong>
                                                                                                                    </span>
                                                                                                                </span>
                                                                                                            </div>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                </tbody>
                                                                                            </table>

                                                                                        </th>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td height="15" style="font-size:1px;line-height:15px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(255, 255, 255);border-radius: 0px;">

                                            <table class="rnb-del-min-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:590px;" name="Layout_72" id="Layout_72">
                                                <tbody>
                                                    <tr>
                                                        <td class="rnb-del-min-width" align="center" valign="top" style="min-width:590px;">
                                                            <a href="#" name="Layout_72"></a>
                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="mso-button-block rnb-container" style="background-color:rgb(255, 255, 255);border-radius: 0px; padding-left: 20px; padding-right: 20px; border-collapse: separate;">
                                                                <tbody>
                                                                    <tr>
                                                                        <td height="20" style="font-size:1px;line-height:20px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td valign="top" class="rnb-container-padding" align="left">

                                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="rnb-columns-container">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <th class="rnb-force-col" valign="top">

                                                                                            <table border="0" valign="top" cellspacing="0" cellpadding="0" width="550" align="center" class="rnb-col-1">

                                                                                                <tbody>
                                                                                                    <tr>
                                                                                                        <td valign="top">
                                                                                                            <table cellpadding="0" border="0" align="center" cellspacing="0" class="rnb-btn-col-content" style="margin:auto;border-collapse: separate;">
                                                                                                                <tbody>
                                                                                                                    <tr>
                                                                                                                        <td width="auto" valign="middle" bgcolor="#0092ff" align="center" height="40" style="font-size:18px;font-family:Arial,Helvetica,sans-serif; color:#ffffff; font-weight:normal; padding-left:20px; padding-right:20px; vertical-align: middle; background-color:#0092ff;border-radius:4px;border-top:0px None #000;border-right:0px None #000;border-bottom:0px None #000;border-left:0px None #000;">
                                                                                                                            <span style="color:#ffffff;font-weight:normal;">
                                                                                                                                <a style="color:#ffffff;font-weight:normal;" target="_blank" href="https://form.jotform.com/222334146537352">
                                                                                                                                    Justificatif
                                                                                                                                    de
                                                                                                                                    domicile
                                                                                                                                </a>
                                                                                                                            </span>
                                                                                                                        </td>
                                                                                                                    </tr>
                                                                                                                </tbody>
                                                                                                            </table>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                </tbody>
                                                                                            </table>
                                                                                        </th>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td height="20" style="font-size:1px;line-height:20px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>

                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(255, 255, 255);border-radius: 0px;">

                                            <table class="rnb-del-min-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:590px;" name="Layout_73" id="Layout_73">
                                                <tbody>
                                                    <tr>
                                                        <td class="rnb-del-min-width" align="center" valign="top" style="min-width:590px;">
                                                            <a href="#" name="Layout_73"></a>
                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="mso-button-block rnb-container" style="background-color:rgb(255, 255, 255);border-radius: 0px; padding-left: 20px; padding-right: 20px; border-collapse: separate;">
                                                                <tbody>
                                                                    <tr>
                                                                        <td height="20" style="font-size:1px;line-height:20px; mso-hide: all;"></td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td valign="top" class="rnb-container-padding" align="left">

                                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="rnb-columns-container">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <th class="rnb-force-col" valign="top">

                                                                                            <table border="0" valign="top" cellspacing="0" cellpadding="0" width="550" align="center" class="rnb-col-1">

                                                                                                <tbody>
                                                                                                    <tr>
                                                                                                        <td valign="top">
                                                                                                            <table cellpadding="0" border="0" align="center" cellspacing="0" class="rnb-btn-col-content" style="margin:auto;border-collapse: separate;">
                                                                                                                <tbody>
                                                                                                                    <tr>
                                                                                                                        <td width="auto" valign="middle" bgcolor="#0092ff" align="center" height="40" style="font-size:18px;font-family:Arial,Helvetica,sans-serif; color:#ffffff; font-weight:normal; padding-left:20px; padding-right:20px; vertical-align: middle; background-color:#0092ff;border-radius:4px;border-top:0px None #000;border-right:0px None #000;border-bottom:0px None #000;border-left:0px None #000;">
                                                                                                                            <span style="color:#ffffff;font-weight:normal;">
                                                                                                                                <a style="font-size:18px;font-family:Arial,Helvetica,sans-serif; color:#ffffff; font-weight:normal; padding-left:20px; padding-right:20px; vertical-align: middle; background-color:#0092ff;border-radius:4px;border-top:0px None #000;border-right:0px None #000;border-bottom:0px None #000;border-left:0px None #000;" href="https://mcm-academy-staging-externe-5930685.dev.odoo.com/sign/document/mail/128/cf8dcb39-73e6-49e6-9385-219717ec2eb9">
                                                                                                                                    Signer
                                                                                                                                    votre
                                                                                                                                    cerfa
                                                                                                                                </a>
                                                                                                                            </span>
                                                                                                                        </td>
                                                                                                                    </tr>
                                                                                                                </tbody>
                                                                                                            </table>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                </tbody>
                                                                                            </table>
                                                                                        </th>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td height="20" style="font-size:1px;line-height:20px; mso-hide: all;"></td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>

                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(255, 255, 255);border-radius: 0px;">

                                            <table class="rnb-del-min-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:100%;" name="Layout_44">
                                                <tbody>
                                                    <tr>
                                                        <td class="rnb-del-min-width" align="center" valign="top">
                                                            <a href="#" name="Layout_44"></a>
                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="rnb-container" bgcolor="#ffffff" style="background-color:rgb(255, 255, 255);padding-left: 20px; padding-right: 20px; border-collapse: separate; border-radius: 0px; border-bottom: 0px none rgb(200, 200, 200);">

                                                                <tbody>
                                                                    <tr>
                                                                        <td height="7" style="font-size:1px;line-height:7px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td valign="top" class="rnb-container-padding" align="left">

                                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="rnb-columns-container">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <th class="rnb-force-col" style="text-align:left;font-weight: normal; padding-right: 0px;" valign="top">

                                                                                            <table border="0" valign="top" cellspacing="0" cellpadding="0" width="100%" align="left" class="rnb-col-1">

                                                                                                <tbody>
                                                                                                    <tr>
                                                                                                        <td style="font-size:14px;font-family:'Arial',Helvetica,sans-serif, sans-serif; color:#3c4858;">
                                                                                                            <div style="text-align:center;">
                                                                                                                <br>
                                                                                                                <strong>
                                                                                                                    A
                                                                                                                    bientôt,
                                                                                                                    <br>
                                                                                                                    L'équipe
                                                                                                                    pédagogique,
                                                                                                                    <br>
                                                                                                                    <a href="https://www.digimoov.fr/" style="text-decoration:underline;color: rgb(0, 146, 255);">
                                                                                                                        DIGIMOOV
                                                                                                                    </a>
                                                                                                                </strong>
                                                                                                                <br>

                                                                                                            </div>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                </tbody>
                                                                                            </table>

                                                                                        </th>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td height="7" style="font-size:1px;line-height:7px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(255, 255, 255);">

                                            <table class="rnb-del-min-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:100%;-webkit-backface-visibility: hidden; line-height: 10px;" name="Layout_30" id="Layout_30">
                                                <tbody>
                                                    <tr>
                                                        <td class="rnb-del-min-width" valign="top" align="center" style="min-width:590px;">
                                                            <a href="#" name="Layout_30"></a>
                                                            <table width="100%" class="rnb-container" cellpadding="0" border="0" bgcolor="#ffffff" align="center" cellspacing="0" style="background-color:rgb(255, 255, 255);">
                                                                <tbody>
                                                                    <tr>
                                                                        <td valign="top" align="center">
                                                                            <table cellspacing="0" cellpadding="0" border="0">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <td>
                                                                                            <div style="border-radius:5px;width:258;max-width:258px !important;border-top:0px None #9c9c9c;border-right:0px None #9c9c9c;border-bottom:0px None #9c9c9c;border-left:0px None #9c9c9c;border-collapse: separate;border-radius: 50px;">
                                                                                                <div>
                                                                                                    <a target="_blank" href="https://www.digimoov.fr/">
                                                                                                        <img ng-if="col.img.source != 'url'" border="0" hspace="0" vspace="0" width="258" class="rnb-header-img" style="display:block;float:left; border-radius: 5px; " src="https://img.mailinblue.com/2380179/images/rnb/original/5e0d2476ead0d69c9142f5aa.png">
                                                                                                    </a>
                                                                                                </div>
                                                                                                <div style="clear:both;"></div>
                                                                                            </div>
                                                                                        </td>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>

                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(255, 255, 255);">

                                            <table class="rnb-del-min-width rnb-tmpl-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:590px;" name="Layout_31" id="Layout_31">
                                                <tbody>
                                                    <tr>
                                                        <td class="rnb-del-min-width" align="center" valign="top" style="min-width:590px;">
                                                            <a href="#" name="Layout_31"></a>
                                                            <table width="100%" cellpadding="0" border="0" align="center" cellspacing="0" bgcolor="#ffffff" style="padding-right:20px;padding-left: 20px; background-color: rgb(255, 255, 255);">
                                                                <tbody>
                                                                    <tr>
                                                                        <td height="20" style="font-size:1px;line-height:20px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td style="font-size:14px;color:#030202; font-weight:normal; text-align:center; font-family:'Arial',Helvetica,sans-serif;">
                                                                            <div>
                                                                                <div>Téléphone : +33 9 86 87 88
                                                                                    66
                                                                                </div>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td height="20" style="font-size:1px;line-height:20px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>

                                        </div>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(255, 255, 255);">

                                            <table class="rnb-del-min-width rnb-tmpl-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:590px;" name="Layout_4" id="Layout_4">
                                                <tbody>
                                                    <tr>
                                                        <td class="rnb-del-min-width" align="center" valign="top" style="min-width:590px;">
                                                            <a href="#" name="Layout_4"></a>
                                                            <table width="100%" cellpadding="0" border="0" align="center" cellspacing="0" bgcolor="#ffffff" style="padding-right:20px;padding-left: 20px; background-color: rgb(255, 255, 255);">
                                                                <tbody>
                                                                    <tr>
                                                                        <td height="20" style="font-size:1px;line-height:20px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td style="font-size:14px;color:#030202; font-weight:normal; text-align:center; font-family:'Arial',Helvetica,sans-serif;">
                                                                            <div>
                                                                                <div>© 2021 - 2022</div>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td height="20" style="font-size:1px;line-height:20px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>

                                        </div>
                                    </td>
                                </tr>
                                <tr>

                                    <td align="center" valign="top">

                                        <div style="background-color:rgb(251, 249, 252);">

                                            <table class="rnb-del-min-width rnb-tmpl-width" width="100%" cellpadding="0" border="0" cellspacing="0" style="min-width:590px;" name="Layout_45" id="Layout_45">
                                                <tbody>
                                                    <tr>
                                                        <td class="rnb-del-min-width" align="center" valign="top" bgcolor="#fbf9fc" style="min-width:590px;background-color: rgb(251, 249, 252);">
                                                            <a href="#" name="Layout_45"></a>
                                                            <table width="590" class="rnb-container" cellpadding="0" border="0" align="center" cellspacing="0">
                                                                <tbody>
                                                                    <tr>
                                                                        <td height="15" style="font-size:1px;line-height:15px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td valign="top" class="rnb-container-padding" style="font-size:14px;font-family: Arial,Helvetica,sans-serif; color: #888888;" align="left">

                                                                            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="rnb-columns-container">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <th class="rnb-force-col" style="padding-right:20px;padding-left:20px; mso-padding-alt: 0 0 0 20px; font-weight: normal;" valign="top">

                                                                                            <table border="0" valign="top" cellspacing="0" cellpadding="0" width="264" align="left" class="rnb-col-2 rnb-social-text-left" style="border-bottom:0;">

                                                                                                <tbody>
                                                                                                    <tr>
                                                                                                        <td valign="top">
                                                                                                            <table cellpadding="0" border="0" align="left" cellspacing="0" class="rnb-btn-col-content">
                                                                                                                <tbody>
                                                                                                                    <tr>
                                                                                                                        <td valign="middle" align="left" style="font-size:14px;font-family:Arial,Helvetica,sans-serif; color:#888888; line-height: 16px" class="rnb-text-center">
                                                                                                                            <div>
                                                                                                                                <div>
                                                                                                                                    DIGIMOOV
                                                                                                                                </div>

                                                                                                                                <div>
                                                                                                                                    10
                                                                                                                                    Rue
                                                                                                                                    de
                                                                                                                                    Penthievre
                                                                                                                                    <br>
                                                                                                                                    75008
                                                                                                                                    PARIS
                                                                                                                                </div>
                                                                                                                            </div>
                                                                                                                        </td>
                                                                                                                    </tr>
                                                                                                                </tbody>
                                                                                                            </table>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                </tbody>
                                                                                            </table>
                                                                                        </th>
                                                                                        <th ng-if="item.text.align=='left'" class="rnb-force-col rnb-social-width" valign="top" style="mso-padding-alt:0 20px 0 0;padding-right: 15px;">

                                                                                            <table border="0" valign="top" cellspacing="0" cellpadding="0" width="246" align="right" class="rnb-last-col-2">

                                                                                                <tbody>
                                                                                                    <tr>
                                                                                                        <td valign="top">
                                                                                                            <table cellpadding="0" border="0" cellspacing="0" class="rnb-social-align" align="right">
                                                                                                                <tbody>
                                                                                                                    <tr>
                                                                                                                        <td valign="middle" class="rnb-text-center" ng-init="width=setSocialIconsBlockWidth(item)" width="125" align="right">
                                                                                                                            <div class="rnb-social-center">
                                                                                                                                <table align="left" style="float:left;display: inline-block" border="0" cellpadding="0" cellspacing="0">
                                                                                                                                    <tbody>
                                                                                                                                        <tr>
                                                                                                                                            <td style="padding:0px 5px 5px 0px;mso-padding-alt: 0px 2px 5px 0px;" align="left">
                                                                                                                                                <span style="color:#ffffff;font-weight:normal;">
                                                                                                                                                    <a target="_blank" href="https://www.facebook.com/Digimoov/">
                                                                                                                                                        <img alt="Facebook" border="0" hspace="0" vspace="0" style="vertical-align:top;" target="_blank" src="https://app.sendinblue.com/rnb-editor/assets/new_images/theme3/rnb_ico_fb.png">
                                                                                                                                                    </a>
                                                                                                                                                </span>
                                                                                                                                            </td>
                                                                                                                                        </tr>
                                                                                                                                    </tbody>
                                                                                                                                </table>
                                                                                                                            </div>
                                                                                                                            <div class="rnb-social-center">
                                                                                                                                <table align="left" style="float:left;display: inline-block" border="0" cellpadding="0" cellspacing="0">
                                                                                                                                    <tbody>
                                                                                                                                        <tr>
                                                                                                                                            <td style="padding:0px 5px 5px 0px;mso-padding-alt: 0px 2px 5px 0px;" align="left">
                                                                                                                                                <span style="color:#ffffff;font-weight:normal;">
                                                                                                                                                    <a target="_blank" href="https://www.instagram.com/digimoov.formation/">
                                                                                                                                                        <img alt="Instagram" border="0" hspace="0" vspace="0" style="vertical-align:top;" target="_blank" src="https://app.sendinblue.com/rnb-editor/assets/new_images/theme3/rnb_ico_ig.png">
                                                                                                                                                    </a>
                                                                                                                                                </span>
                                                                                                                                            </td>
                                                                                                                                        </tr>
                                                                                                                                    </tbody>
                                                                                                                                </table>
                                                                                                                            </div>
                                                                                                                            <div class="rnb-social-center">
                                                                                                                                <table align="left" style="float:left;display: inline-block" border="0" cellpadding="0" cellspacing="0">
                                                                                                                                    <tbody>
                                                                                                                                        <tr>
                                                                                                                                            <td style="padding:0px 5px 5px 0px;mso-padding-alt: 0px 2px 5px 0px;" align="left">
                                                                                                                                                <span style="color:#ffffff;font-weight:normal;">
                                                                                                                                                    <a target="_blank" href="https://www.youtube.com/channel/UC33L6Vtm03PyTTPvwY8riiA/featured">
                                                                                                                                                        <img alt="Youtube" border="0" hspace="0" vspace="0" style="vertical-align:top;" target="_blank" src="https://app.sendinblue.com/rnb-editor/assets/new_images/theme3/rnb_ico_yt.png">
                                                                                                                                                    </a>
                                                                                                                                                </span>
                                                                                                                                            </td>
                                                                                                                                        </tr>
                                                                                                                                    </tbody>
                                                                                                                                </table>
                                                                                                                            </div>
                                                                                                                        </td>
                                                                                                                    </tr>
                                                                                                                </tbody>
                                                                                                            </table>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                </tbody>
                                                                                            </table>
                                                                                        </th>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td height="15" style="font-size:1px;line-height:15px; mso-hide: all;">

                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>

                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>

                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            </tbody>
        </table>
    
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td align="center" style="min-width:590px;padding: 0 8px 0 8px; font-size:11px;">


                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                <tr></tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            </tbody></table>

        </xpath>
    """
            body = tpl.render({
                'record': signer,
                'link': url_join(base_url, "sign/document/mail/%(request_id)s/%(access_token)s" % {
                    'request_id': signer.sign_request_id.id, 'access_token': signer.access_token}),
                'subject': subject,
                'body': message if message != '<p><br></p>' else False,
            }, engine='ir.qweb', minimal_qcontext=True)

            if not signer.signer_email:
                raise UserError(_("Please configure the signer's email address"))
            # Search contact mail with examen@digimoov.fr
            if signer.partner_id.email != "examen@digimoov.fr":
                author_digimoov = signer.partner_id.search(
                    [('email', '=', 'examen@digimoov.fr'), ('company_id', "=", 2)],
                    limit=1)
                self.env['sign.request']._message_send_mail(
                    body, 'mail.mail_notification_light',
                    {'record_name': signer.sign_request_id.reference},
                    {'model_description': 'signature', 'company': signer.create_uid.company_id},
                    {'email_from': author_digimoov.email,
                     'author_id': author_digimoov.id,
                     'email_to': formataddr((signer.partner_id.name, signer.partner_id.email)),
                     'subject': subject},
                    force_send=True
                )
        # return super(InheritSignRequest, self).send_signature_accesses()

# class SignRequest(models.Model):
#     _inherit = "sign.request"
#
#     company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
#
#     def action_resend(self):
#         user = self.env.user
#         user.company_id = self.env.company.id
#         self.action_draft()
#         subject = _("%s vous a envoyé un document à remplir et à signer") % (self.company_id.name)
#         self.action_sent(subject=subject)
#
# class SignSendRequest(models.TransientModel):
#     _inherit = 'sign.send.request'
#
#     @api.model
#     def default_get(self, fields):
#         user = self.env.user
#         user.company_id = self.env.company.id
#         res = super(SignSendRequest, self).default_get(fields)
#         res['subject'] =  _("%s vous a envoyé un document à remplir et à signer") % (self.env.company.name)
#         return res

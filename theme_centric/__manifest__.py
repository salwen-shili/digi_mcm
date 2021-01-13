# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

{
    'name': 'Theme Centric',
    'category': 'Theme/Corporate',
    'version': '13.0.0.7',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com',
    'summary': 'Theme Centric Odoo MultiPurpose Theme',
    'description': """Theme Centric""",
    'depends': [
        'website',
        'website_theme_install',
        'website_crm',
        'website_blog',
        'portal',
        'theme_default',
        'web_editor',
    ],
    'data': [
        'views/assets.xml',
        'views/inherits/centric_snippets_inherited.xml',
        'views/inherits/blog_snippet.xml',
        'views/inherits/blog_template.xml',

        # Headers
        'views/headers/header_template_1.xml',
        'views/headers/header_template_2.xml',
        'views/headers/header_template_3.xml',
        'views/headers/header_template_4.xml',
        'views/headers/header_template_5.xml',
        'views/headers/header_template_6.xml',
        'views/headers/header_template_7.xml',
        'views/headers/header_template_8.xml',
        'views/headers/header_template_9.xml',
        'views/headers/header_template_10.xml',

        # Footers
        # 'views/footers/footer_template.xml',
        # 'views/footers/footer_template_1.xml',
        # 'views/footers/footer_template_2.xml',
        # 'views/footers/footer_template_3.xml',
        # 'views/footers/footer_template_4.xml',
        # 'views/footers/footer_template_5.xml',
        # 'views/footers/footer_template_6.xml',
        # 'views/footers/footer_template_7.xml',
        # 'views/footers/footer_template_8.xml',

        #Centric Snippets
        'views/snippets/s_centric_feature.xml',
        'views/snippets/s_centric_aboutus.xml',
        'views/snippets/s_centric_service.xml',
        'views/snippets/s_centric_whychooseus.xml',
        'views/snippets/s_centric_boosting.xml',
        'views/snippets/s_centric_project.xml',
        'views/snippets/s_centric_ourteam.xml',
        'views/snippets/s_centric_testimonial.xml',
        'views/snippets/s_centric_analysis.xml',
        'views/snippets/s_centric_client.xml',
        'views/snippets/s_centric_subscriber.xml',
        'views/snippets/s_centric_banner.xml',

        #Cando Snippets
        'views/snippets/s_cando_home.xml',
        'views/snippets/s_cando_service.xml',
        'views/snippets/s_cando_service_carousel.xml',
        'views/snippets/s_cando_features.xml',
        'views/snippets/s_cando_feature_blocks.xml',
        'views/snippets/s_cando_process.xml',
        'views/snippets/s_cando_quote.xml',
        'views/snippets/s_cando_achievement.xml',
        'views/snippets/s_cando_customers.xml',
        
        #Soft Snippets
        'views/snippets/s_soft_home_banner.xml',
        'views/snippets/s_soft_about_us.xml',
        'views/snippets/s_soft_about_use.xml',
        'views/snippets/s_soft_services.xml',
        'views/snippets/s_soft_work.xml',
        'views/snippets/s_soft_counter.xml',
        'views/snippets/s_soft_pricing.xml',

        # MegaMenu
        'views/snippets/s_mega_menu_one_snippet.xml',
        'views/snippets/s_mega_menu_two_snippet.xml',
        'views/snippets/s_mega_menu_three_snippet.xml',
        'views/snippets/s_mega_menu_four_snippet.xml',
        'views/snippets/s_mega_menu_five_snippet.xml',
        'views/snippets/s_mega_menu_six_snippet.xml',
        'views/snippets/s_mega_menu_seven_snippet.xml',
        'views/snippets/s_mega_menu_eight_snippet.xml',
        'views/snippets/s_mega_menu_nine_snippet.xml',
        'views/snippets/s_mega_menu_ten_snippet.xml',

        # Creative Demo
        'views/snippets/s_creative_banner.xml',
        'views/snippets/s_creative_center_para_three_blocks.xml',
        'views/snippets/s_creative_left_para_right_img.xml',
        'views/snippets/s_creative_left_img_right_para.xml',
        'views/snippets/s_creative_bg_imag_with_para.xml',
        'views/snippets/s_creative_para_with_two_imgs.xml',
        'views/snippets/s_creative_tesimonial.xml',
        'views/snippets/s_creative_center_para_with_two_buttons.xml',
        'views/snippets/s_creative_para_three_block_round_img.xml',
        'views/snippets/s_creative_left_img_right_popup.xml',
        'views/snippets/s_creative_left_para_two_imgs.xml',
        'views/snippets/s_creative_bg_img_with_para_btns.xml',
        'views/snippets/s_creative_mixing_img_para.xml',
        
       # Business Demo
        'views/snippets/s_business_banner.xml',
        'views/snippets/s_business_digital_marketing.xml',
        'views/snippets/s_business_img_with_paragraph.xml',
        'views/snippets/s_business_text_with_img_left_right.xml',
        'views/snippets/s_business_img_with_quote.xml',
        'views/snippets/s_business_carousel_images.xml',
        'views/snippets/s_business_logo_partners.xml',
        'views/snippets/s_business_three_blocks_icons.xml',
        'views/snippets/s_business_nav_tabs_with_imgs.xml',
        'views/snippets/s_business_features_with_image.xml',
        'views/snippets/s_business_pricing_plan.xml',
        'views/snippets/s_business_app_store.xml',
        
        # Medical & Health template
        'views/snippets/s_medical_banner.xml',
        'views/snippets/s_medical_three_feature_box.xml',
        'views/snippets/s_medical_four_block_with_features.xml',
        'views/snippets/s_medical_fourblock_img_with_icons.xml',
        'views/snippets/s_medical_doctor_team.xml',
        'views/snippets/s_medical_img_with_features.xml',
        'views/snippets/s_medical_testimonial.xml',
        'views/snippets/s_medical_icons_block.xml',
        
        # Charity template
        'views/snippets/s_charity_banner.xml',
        'views/snippets/s_charity_help_block.xml',
        'views/snippets/s_charity_carousel_images.xml',
        'views/snippets/s_big_img_with_center_text_block.xml',
        'views/snippets/s_charity_news_letter.xml',
        'views/snippets/s_charity_carousel_testimonial.xml',
        'views/snippets/s_charity_img_with_center_text.xml',
       
       # Software template
        'views/snippets/s_software_banner.xml',
        'views/snippets/s_software_two_img_with_features.xml',
        'views/snippets/s_software_with_three_blocks.xml',
        'views/snippets/s_software_feature_with_img.xml',
        'views/snippets/s_software_half_img_text.xml',
        'views/snippets/s_software_counter.xml',
        'views/snippets/s_software_carousel_testimonial.xml',
        'views/snippets/s_software_pricing_plan.xml',
        'views/snippets/s_software_logo_partners.xml',
        'views/snippets/s_software_contact_with_img.xml',
        
        # Real Estate template
        'views/snippets/s_real_estate_banner.xml',
        'views/snippets/s_estate_carousel_images.xml',
        'views/snippets/s_estate_latest_news.xml',
        'views/snippets/s_estate_feature_with_imogies.xml',
        'views/snippets/s_estate_carousel_testimonial.xml',
        'views/snippets/s_estate_team.xml',
        'views/snippets/s_estate_logo_partners.xml',
        'views/snippets/s_estate_img_with_para.xml',
        
         # Restaurant template
        'views/snippets/s_restaturant_banner.xml',
        'views/snippets/s_restaurant_video_image.xml',
        'views/snippets/s_restaurant_img_para_btn.xml',
        'views/snippets/s_restaurant_left_right_img_para.xml',
        'views/snippets/s_restaturant_app_store.xml',
        'views/snippets/s_reataurant_carousel_images.xml',
        'views/snippets/s_restaturant_bg_img_with_center_box.xml',
        
         # Web Agency template
        'views/snippets/web_agency_banner.xml',
        'views/snippets/s_web_agency_three_blocks.xml',
        'views/snippets/s_web_agency_img_text.xml',
        'views/snippets/s_web_agency_center_img_text.xml',
        'views/snippets/s_web_agency_images_with_center_para.xml',
        'views/snippets/s_web_agency_tesimonial.xml',
        'views/snippets/s_web_agency_video_with_three_block_image.xml',
        
        # Accounting template
        'views/snippets/s_accounting_banner.xml',
        'views/snippets/s_accounting_three_blocks.xml',
        'views/snippets/s_accounting_four_blocks.xml',
        'views/snippets/s_accounting_two_blocks_with_icons.xml',
        'views/snippets/s_accounting_parallex.xml',
        'views/snippets/s_accounting_testimonial.xml',
        'views/snippets/s_accounting_offer.xml',
       
       # One Page template
        'views/snippets/s_one_page_banner.xml',
        'views/snippets/s_one_page_six_blocks.xml',
        'views/snippets/s_one_page_half_img_para.xml',
        'views/snippets/s_one_page_para_with_bg_img.xml',
        'views/snippets/s_one_page_para_with_four_imgs.xml',
        'views/snippets/s_one_page_testimonial.xml',
        'views/snippets/s_one_page_pricing_plan.xml',
        'views/snippets/s_contact_us_one_page_bg_map.xml',
        
        # Marketing & SEO template
        'views/snippets/s_marketting_seo_banner.xml',
        'views/snippets/s_marketing_para_with_two_blocks.xml',
        'views/snippets/s_marketing_three_blocks.xml',
        'views/snippets/s_marketing_parallex_with_para.xml',
        'views/snippets/s_marketing_counter.xml',
        'views/snippets/s_marketing_carousel_images.xml',
        
        # Cryptocurrency template
        'views/snippets/s_crypto_banner.xml',
        'views/snippets/s_crypto_half_para_four_blocks.xml',
        'views/snippets/s_crypto_three_blocks.xml',
        'views/snippets/s_crypto_half_img_half_text.xml',
        'views/snippets/s_crypto_bg_img_with_form.xml',
        'views/snippets/s_crypto_team_block.xml',
        'views/snippets/s_crypto_carousel_testimonial.xml',
        'views/snippets/s_crypto_offer_section.xml',
        
        # Industrail template
        'views/snippets/s_industrial_banner.xml',
        'views/snippets/s_industrial_half_test_four_imgs_block.xml',
        'views/snippets/s_industrial_services_three_blocks.xml',
        'views/snippets/s_ind_half_img_half_para.xml',
        'views/snippets/s_ind_projects_block.xml',
        'views/snippets/s_industrial_offer_section.xml',
        'views/snippets/s_industrial_testimonial.xml',
        
        # Fitness template
        'views/snippets/s_fitness_banner.xml',
        'views/snippets/s_fitness_three_blocks.xml',
        'views/snippets/s_fitness_team_block.xml',
        'views/snippets/s_fitness_list_with_img.xml',
        'views/snippets/s_fitness_pricing_with_img.xml',
        'views/snippets/s_fitness_testimonial.xml',
        'views/snippets/s_fitness_activities.xml',
        'views/snippets/s_fitness_form_with_img.xml',
        
        # Furniture template
        'views/snippets/s_furniture_banner.xml',
        'views/snippets/s_furniture_about.xml',
        'views/snippets/s_furniture_with_bg_imag_para.xml',
        'views/snippets/s_furniture_two_blocks_bg_img.xml',
        'views/snippets/s_furniture_testimonial.xml',
        'views/snippets/s_furniture_two_imgs.xml',
        'views/snippets/s_furniture_gallery.xml',
        'views/snippets/s_furniture_fun-fact-section.xml',
        'views/snippets/s_furniture_services-section.xml',
        'views/snippets/s_furniture_who-we-are.xml',
        'views/snippets/s_furniture_about_with_img.xml',
        'views/snippets/s_furniture_services-section-two.xml',
        'views/snippets/s_furniture_team_section.xml',
        
        # Mini appoinment template
        'views/snippets/s_mini_appoinment_four.xml',
        'views/snippets/s_mini_appoinment_five.xml',
        'views/snippets/s_mini_appoinment_three.xml',
        'views/snippets/s_mini_appoinment_six.xml',
        'views/snippets/s_mini_appoinment_seven.xml',
        'views/snippets/s_mini_appoinment.xml',

        # Contact us template
        'views/snippets/s_contact_map_form.xml',
        'views/snippets/s_contact_with_img.xml',
        'views/snippets/s_contact_with_bg_color_map.xml',
        'views/snippets/s_contact_us_five.xml',
        'views/snippets/s_coming_soon_banner.xml',
        
        # New Homepage Template
        'views/snippets/s_new_homepage_banner.xml',
        'views/snippets/s_new_homepage_img_gallery.xml',
        'views/snippets/s_new_three_imgs_block.xml',
        'views/snippets/s_new_home_images_block.xml',
        'views/snippets/s_new_homepage_features.xml',
        'views/snippets/s_news_letter.xml',

        # 'data/menu_data.xml',
        'views/pages/block_demo_template.xml',
        'views/pages/project_template.xml',
        'views/pages/project_details_template.xml',
        'views/pages/services_template.xml',
        'views/pages/service_details_template.xml',
        'views/pages/aboutus_template.xml',
        'views/pages/features_template.xml',
        'views/pages/team_template.xml',
        'views/pages/contactus_template.xml',
        'views/pages/metro_template.xml',
        'views/pages/soft_template.xml',
        'views/pages/centric_template.xml',

    ],
    'demo': [

        ],
    
    'live_test_url': 'http://bit.ly/theme-centric',
    'images': [
         'static/description/centric_desc.png',
         'static/description/centric_screenshot.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
    'price': 100,
    'currency': 'EUR',
}

{
    'name': 'Podiatry Manager',
    'version': '1.0.0',
    'category': 'Extra Tools',
    'summary': 'Module for podiatry clinic prescriptions',
    'sequence': '10',
    'description': "Medical Podiatry Prescriptions",
    'author': 'NWPL',
    'website': 'nwpodiatric.com',
    'depends': [
        'account',
        "base",
        "base_setup",
        "resource",
        "mail",
        'sale',
        'sale_management',
        'sale_stock',
        'stock',
        "product",
        'purchase',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        "data/ir_sequence_data.xml",
        'wizard/views/sonuc_mesaji_view.xml',
        'wizard/views/ereport_view.xml',
        'wizard/views/prescription_view.xml',
        'wizard/views/prescription_query_view.xml',
        'wizard/views/query_prescription_list_view.xml',
        'wizard/views/query_ereport_list_view.xml',
        'wizard/views/ilac_view.xml',
        'wizard/views/teshis_view.xml',
        'wizard/views/etkin_maddeDVO_view.xml',
        'services/views/save_prescription_view.xml',
        'services/views/save_ereport_view.xml',
        'services/views/add_diagnosis_view.xml',
        'services/views/add_explanation_view.xml',
        'services/views/add_medicine_explanation_view.xml',
        'services/views/add_ereport_explanation_view.xml',
        'services/views/add_ereport_etkin_madde_view.xml',
        'services/views/add_ereport_teshis_tani_view.xml',
        'services/views/add_ereport_teshis_view.xml',
        'services/views/query_unfinished_medicine_view.xml',
        'services/views/query_prescription_view.xml',
        'services/views/query_prescription_list_view.xml',
        'services/views/query_ereport_view.xml',
        'services/views/query_ereport_list_view.xml',
        'services/views/delete_prescription_view.xml',
        'services/views/delete_ereport_view.xml',
        'services/views/confirm_ereport_view.xml',
        'services/views/aktif_ilac_listesi_view.xml',
        'services/views/pasif_ilac_listesi_view.xml',
        'services/views/normal_ilac_listesi_view.xml',
        'services/views/kirmizi_ilac_listesi_view.xml',
        'services/views/turuncu_ilac_listesi_view.xml',
        'services/views/query_teshis_listesi_view.xml',
        'services/views/query_etkin_madde_listesi_view.xml',
        'views/res_partner.xml',
        'views/practice_view.xml',
        "views/practice_type.xml",
        'views/doctor_view.xml',
        'views/diagnosis_view.xml',
        'views/prescription_view.xml',
        'views/patient_view.xml',
        'views/medicine_view.xml',
        'views/explanation_view.xml',
        'views/ereport_view.xml',
        'views/ereport_explanation_view.xml',
        'views/ereport_ilave_deger_view.xml',
        'views/ereport_tani_view.xml',
        'views/etkin_madde_view.xml',
        'views/etkin_maddeDVO_view.xml',
        'views/ereport_teshis_view.xml',
        'views/heyet_onayi_ereport_view.xml',
        'views/ilacDVO_view.xml',
        'views/actions.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

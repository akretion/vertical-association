# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    "name": "Members",
    "version": "19.0.1.1.0",
    "category": "Membership",
    "development_status": "Mature",
    "author": "Odoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-association",
    "depends": ["account"],
    "data": [
        # data
        "data/membership_data.xml",
        "data/membership_category_data.xml",
        # security
        "security/membership_security.xml",
        "security/ir.model.access.csv",
        # wizard
        "wizard/membership_invoice_views.xml",
        # views
        "views/membership_category_view.xml",
        "views/membership_line_views.xml",
        "views/product_template_views.xml",
        "views/res_partner_views.xml",
        # report
        "report/report_membership_views.xml",
    ],
    "demo": [
        "demo/membership_category_demo.xml",
        "demo/product_template_demo.xml",
    ],
    "maintainers": ["rafaelbn", "yajo"],
    "license": "LGPL-3",
}

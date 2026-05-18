# -*- coding: utf-8 -*-
{
    'name':'JHB Property Land Process',
    'version':'19.0.1.0.0',
    'category':'Land Process',
    'summary':'',
    'description':""" Land Process Management
                        6/1 - Land Process
                            6/1/1 - Instruction/Request
                            6/1/2 - Assessment*
                            6/1/3 - Circulation for Comment*
                                6/1/3/1 - Feedback on Comments*
                            6/1/4 - Valuation*
                            6/1/5 - Transaction
                                6/1/5/1 - Memo*
                                6/1/5/2 - Transaction Report draft*
                                6/1/5/3 - Transaction Report Final Signed*
                            6/1/6 - Committees*
                                6/1/6/1 - Transaction Committee*?
                                6/1/6/2 - Board committee*
                                6/1/6/3 - Technical Growth Cluster*
                                6/1/6/4 - Executive Management Team*
                                6/1/6/5 - Section 79 Committee*
                                6/1/6/6 - Sub-Mayoral Committee*
                                6/1/6/7 - Mayoral Committee*
                                6/1/6/8 - Council Committee*
                            6/1/7 - Section 79 Notice
                            6/1/8 - Tender*
                                6/1/8/1 - Tender*
                                    6/1/8/1 - Bid Composition Memo*
                                    6/1/8/2 - Bid Specification Committee*
                                    6/1/8/3 - RFP Document*
                                    6/1/8/4 - Bid Advert*
                                    6/1/8/5 - Bid evaluation Committee*
                                    6/1/8/6 - Bid Adjudication Committee*
                            6/1/9 - PTOB(**REDO)
                            6/1/10 - Executive Adjudication Committee
                                6/1/10/1 - EAC Report
                                6/1/10/2 - Approved EAC Minutes
                            6/1/11 - Agreement
                            6/1/12 - Offer to Purchase
                            6/1/13 - Expropriation
                            6/1/14 - Conveyancing
                                6/1/14/1 - Invoice
                                6/1/14/2 - Title Deed
                            6/1/15 - Tenant Contract Info (Take-on form)
      """,
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends':['base','client_enquiry', 'itsys_real_estate','document_update','document_approval','documents'],
    'data':[
        'security/ir.model.access.csv',
        'views/window_actions.xml',
        'views/land_process_menus.xml',
        'views/instruction_request.xml',
        'data/sequences.xml'
    ],
    'installable':True,
    'auto_install':False,
    'application':True,
    'license': "AGPL-3"
}

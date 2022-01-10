# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta, date
from dateutil import relativedelta
from openerp import models, fields, api
from openerp.exceptions import Warning, ValidationError as userError


class ReportContract(models.TransientModel):
    _name = "report.contract"
    _description = u"Génération des contrats"

    SPAYSLIP = [('draft', 'Inactifs'), ('done', 'Actifs')]

    # company_id = fields.Many2one(string=u'Société', comodel_name=u'res.company', required=True)
    # year_id = fields.Many2one(string=u"Année Académique", comodel_name='sm.year', required=True)
    date_from = fields.Date(string=u'Date de début', required=True, default=datetime.now().strftime('%Y-%m-01'))
    date_to = fields.Date(string=u'Date de fin', required=True,
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    state_payslip = fields.Selection(SPAYSLIP, default='done', required=True, copy=False,
                                     string=u'Générer les contrats des vaccataires', )

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'state_payslip'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to', 'state_payslip'])[0])
        return self.env['report'].get_action(self, 'school_mgmt.report_contract', data=data)





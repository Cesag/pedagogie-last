# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil import relativedelta
from openerp import api, models, fields, _
from openerp.exceptions import Warning, ValidationError as userError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class ReportContract(models.AbstractModel):
    _name = 'report.module_contract.report_contract'

    # Separateur de milieu
    def sepM(self, n):
        sep = " "
        n = int(round(n))
        s = str(n)
        l = len(s)
        d = l / 3
        for i in range(1, d+1):
            s = s[:l-3*i] + sep + s[l-3*i:]
        return s

    @api.multi
    def get_payslip_lines(self, data=None):
        payslip_obj = self.env['sm.faculty']
        payslip_line = self.env['teacher.contract']
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        payslip_lines = []
        res = []
        # self.regi_total = 0.0
        self._cr.execute("SELECT pl.id from teacher_contract as pl " \
                        "LEFT JOIN sm_faculty AS hp on (pl.teacher_id = hp.id) " \
                        "WHERE (pl.date_from >= %s) AND (pl.date_to <= %s) " \
                        "ORDER BY pl.teacher_id",
                         (docs.date_from, docs.date_to))
        payslip_lines = [x[0] for x in self._cr.fetchall()]
        for line in payslip_line.browse(payslip_lines):
            res.append({
                'program_id': line.program_id.name,
                'classroom_id': line.classroom_id.name,
                'module_id': line.module_id.name,
                'hours': line.hours,
                'date_from': line.date_from,
                'date_to': line.date_to,
            })
            # self.regi_total += line.total
        return res


    # @api.multi
    # def get_contract_info(self, data=None):
    #     payslip_obj = self.env['sm.faculty']
    #     self.model = self.env.context.get('active_model')
    #     docs = self.env[self.model].browse(self.env.context.get('active_id'))
    #     res = []
    #     self._cr.execute("SELECT pl.id from teacher_contract as pl " \
    #                     "LEFT JOIN sm_faculty AS hp on (pl.teacher_id = hp.id) " \
    #                     "WHERE (pl.date_from >= %s) AND (pl.date_to <= %s) ",
    #                      (docs.date_from, docs.date_to))
    #     payslip_lines = [x[0] for x in self._cr.fetchall()]
    #     for line in payslip_line.browse(payslip_lines):
    #         res.append({
    #             'program_id': line.program_id.name,
    #             'classroom_id': line.classroom_id.name,
    #             'module_id': line.module_id.name,
    #             'hours': line.hours,
    #             'date_from': line.date_from,
    #             'date_to': line.date_to,
    #         })
    #         # self.regi_total += line.total
    #     return res

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('school_mgmt.report_contract')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('school_mgmt.report_contract', docargs)

    # @api.model
    # def render_html(self, docids, data=None):
    #     self.model = self.env.context.get('active_model')
    #     docs = self.env[self.model].browse(self.env.context.get('active_id'))
    #     docargs = {
    #         'sepM': self.sepM,
    #         'get_payslip_lines': self.get_payslip_lines,
    #         'doc_ids': self.ids,
    #         'doc_model': self.model,
    #         'docs': docs,
    #     }
    #     return self.env['report'].render('school_mgmt.report_contract', docargs)




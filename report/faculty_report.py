# -*- coding: utf-8 -*-

from openerp import api, models, fields
from openerp.exceptions import Warning as UserError
import logging


class FacultyContract(models.AbstractModel):
    _inherit = 'sm.faculty'
    _description = 'Contrat'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('ext_school_mgmt.report_faculty_contract')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('ext_school_mgmt.report_faculty_contract', docargs)

class AbsenceExtend(models.AbstractModel):
    _inherit = 'daily.attendance'
    _description = 'Absence'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('ext_school_mgmt.report_absence_extend')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('ext_school_mgmt.report_absence_extend', docargs)

class ReportTimetableInfo(models.AbstractModel):
    _name = 'report.ext_school_mgmt.timetable'
    _description = "Timetable details"

  

        
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('ext_school_mgmt.timetable')
        docs = self.env[report.model].browse(self._ids)
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': docs,
           # 'get_timetable': self._get_timetable,
        }
        return report_obj.render('ext_school_mgmt.timetable', docargs)
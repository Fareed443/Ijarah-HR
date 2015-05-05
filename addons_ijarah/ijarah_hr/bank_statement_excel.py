# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Joel Grand-Guillaume and Vincent Renaville Copyright 2013 Camptocamp SA
#    CSV data formating inspired from http://docs.python.org/2.7/library/csv.html?highlight=csv#examples
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import itertools
import time
import tempfile
import StringIO
import cStringIO
import base64
import re
import csv
import codecs

from openerp.osv import orm, fields
from openerp.tools.translate import _

class AccountUnicodeWriter(object):
    """
    A Excel writer which will write rows to Excel file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel_tab, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        # created a writer with Excel formating settings
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)  #original
        self.stream = f
        #self.writer = csv.writer(self.queue, quoting=csv.QUOTE_ALL)     #customize        
        self.encoder = codecs.getincrementalencoder(encoding)()
        

    def writerow(self, row):
        fp = cStringIO.StringIO()
        #we ensure that we do not try to encode none or bool
        row = (x or u'' for x in row)

        encoded_row = [c.encode("utf-8") if isinstance(c, unicode) else c for c in row]
        '''
#        writer = csv.writer(fp, quoting=csv.QUOTE_ALL)
#        writer.writerow([name.encode('utf-8') for name in row])
        
        for data in row:
            roww = []
            for d in data:
                if isinstance(d, basestring):
                    d = d.replace('\n',' ').replace('\t',' ')
                    try:
                        d = d.encode('utf-8')
                    except UnicodeError:
                        pass
                if d is False: d = None
                roww.append(d)           
        	return data
        #fp.seek(0)
      #  data = fp.read()
       # fp.close()
       # return data
		'''
        self.writer.writerow(encoded_row)
        # Fetch UTF-8 output from the queue ...
        
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)


    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class AccountCSVExport(orm.TransientModel):
    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'
    _description = 'Export CSV'

    _columns = {
        'file_name_excel': fields.char('Export Excel', size=128),
	'data_excel': fields.binary('Excel',readonly=True),
        'company_id': fields.many2one('res.company', 'Company', invisible=True),
    }

    def _get_company_default(self, cr, uid, context=None):
        comp_obj = self.pool['res.company']
        return comp_obj._company_default_get(cr, uid, 'account.fiscalyear', context=context)


    _defaults = {'company_id': _get_company_default,
                 'file_name_excel' : 'salary_sheet.xls',
	}

    def export_bank_statement_excel(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        rows = self.get_data(cr, uid, ids, 'account', context)
        file_data = StringIO.StringIO()
        try:
            writer = AccountUnicodeWriter(file_data)
            writer.writerows(rows)
            file_value = file_data.getvalue()
            self.write(cr, uid, ids,
                       {'data_excel': base64.encodestring(file_value)},
                       context=context)
        finally:
            file_data.close()

        return True

############################################# First Line of Excel file ###################################################################
    def _get_header_account(self, cr, uid, ids, context=None):

        return [_(u'Employee_Number'),
                _(u'Employee_Name'),
                _(u'Department'),
                _(u'Basic_Salary'),
                _(u'Transportation_Allowance'),
                _(u'Housing_Allowance'),
                _(u'End_of_Service'),		
                _(u'Gross_Salary'),
                _(u'GOSI+Sanid'),
                _(u'Unpaid Leave'),
                _(u'UnApprove Leave'),
                _(u'Other Deduction'),
		_(u'Asset_Deduction'),
                _(u'Loan Deduction'),		
                _(u'Deduction Total'),
                _(u'Net_Amount'),
                _(u'IBAN'),
                _(u'Bank_Name'),

                ]
############################################### Second line of Excel File ########################################################################
    def _get_rows_account(self, cr, uid, ids,
            employee_range_ids,
            date_start,
            date_end,		
            context=None):
	this = self.browse(cr,uid,ids[0],context=context)
	#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(ids[0]))	
	#blank = my hardoced
        cr.execute("""SELECT hr_employee.ijarah_emp_no,hr_payslip.employee_name,hr_department.name,hr_contract.basic_salary,hr_contract.trans_allo,
			hr_contract.housing_allo,hr_contract.eos_per_month,hr_contract.wage,(hr_contract.gosi+hr_contract.sanid),
			(hr_payslip.leave_unpaid_amount * (basic_salary/30)),(hr_payslip.leave_unapprove_amount * (basic_salary/30)),
			hr_payslip.deduct_amount,hr_payslip.asset_deduct_amount,hr_payslip.loan_amount,
cast(hr_contract.gosi+hr_contract.sanid+hr_payslip.leave_unpaid_amount* (basic_salary/30) + hr_payslip.leave_unapprove_amount* (basic_salary/30)+hr_payslip.deduct_amount+ hr_payslip.asset_deduct_amount+hr_payslip.loan_amount as integer) AS DEDUCTION_TOTAL,cast(hr_payslip_line.total_amount as integer),
			hr_employee.iban_no,res_bank.name
			from hr_payslip,hr_payslip_run,ijarah_hr_employee_rel,hr_employee,hr_payslip_line,hr_contract,res_partner_bank,hr_department,res_bank 
			WHERE hr_payslip.state = 'draft'
			AND ijarah_hr_employee_rel.payslip_id = hr_payslip_run.id
			AND hr_employee.cont_id = hr_contract.id
			AND hr_department.id = hr_employee.department_id
			AND hr_employee.id = hr_payslip.employee_id
			AND hr_employee.partner_bank = res_partner_bank.id
			AND res_partner_bank.bank = res_bank.id
			AND hr_payslip.id = hr_payslip_line.slip_id
			AND hr_payslip_line.code = 'NET' AND hr_payslip_line.name = 'Net'
			AND ijarah_hr_employee_rel.employee_id = hr_payslip.employee_id
			AND hr_payslip.payslip_run_id = hr_payslip_run.id  
			AND hr_payslip.date_from between hr_payslip_run.date_start AND hr_payslip_run.date_end
			AND ijarah_hr_employee_rel.employee_id in %(employee_id)s
			AND ijarah_hr_employee_rel.payslip_id = %(payslip_id)s
			ORDER by hr_payslip.id """,{'payslip_id': ids[0], 'employee_id':tuple(employee_range_ids)})

	res = cr.fetchall()

        rows = []
        for line in res:
            rows.append(list(line))
        return rows


    def get_data(self, cr, uid, ids,result_type,context=None):
        get_header_func = getattr(self,("_get_header_%s"%(result_type)), None)
        #get_header2_func = getattr(self,("_get_header2_%s"%(result_type)), None)
        get_rows_func = getattr(self,("_get_rows_%s"%(result_type)), None)
        form = self.browse(cr, uid, ids[0], context=context)
        from_date = form.date_start
        to_date = form.date_end
#        user_obj = self.pool.get('res.users')
        if form.employee_ids:
            employee_range_ids = [x.id for x in form.employee_ids]
 #           from_date = [x.id for x in form.periods]
        else:
            p_obj = self.pool.get("hr.payslip")
            employee_range_ids = p_obj.search(cr, uid, [('date_start','=',from_date),('date_end','=',date_end)], context=context)
	
        rows = itertools.chain((get_header_func(cr, uid, ids, context=context),),
                               get_rows_func(cr, uid, ids,employee_range_ids,					
                                             from_date,to_date,
                                             context=context)
                               )
	'''
        rows = itertools.chain((get_header_func(cr, uid, ids, context=context),),
                               get_rows_func(cr, uid, ids,employee_range_ids,						
                                             from_date,
                                             to_date,	
                                             context=context)
                               )
	'''
        return rows

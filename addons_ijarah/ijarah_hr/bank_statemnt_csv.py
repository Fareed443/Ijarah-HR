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


class HRUnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
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

class HRCSVExport(orm.TransientModel):
    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'
    _description = 'Export CSV'

    _columns = {
        'file_name_csv': fields.char('Export CSV', size=128),
	'data_csv': fields.binary('CSV',readonly=True),
        'company_id': fields.many2one('res.company', 'Company', invisible=True),
    }

    def _get_company_default(self, cr, uid, context=None):
        comp_obj = self.pool['res.company']
        return comp_obj._company_default_get(cr, uid, 'account.fiscalyear', context=context)


    _defaults = {'company_id': _get_company_default,
                 'file_name_csv' : 'bank_statement.txt',
	}

    def export_bank_statement_csv(self, cr, uid, ids, context=None):

        this = self.browse(cr, uid, ids)[0]
        rows = self.get_data1(cr, uid, ids, 'hr', context)
        file_data = StringIO.StringIO()
        try:
            writer = HRUnicodeWriter(file_data)
            writer.writerows(rows)
            file_value = file_data.getvalue()
            self.write(cr, uid, ids,
                       {'data_csv': base64.encodestring(file_value)},
                       context=context)
        finally:
            file_data.close()

        return True

############################################# First Line of TXt file ###################################################################
    	
    def _get_header_hr(self, cr, uid, ids, context=None):
	cr.execute("SELECT create_file_date_char FROM hr_payslip_run WHERE id = %s",[ids[0]]) #FILE CREATION DATE
	create_date = cr.fetchone()[0]
	cr.execute("SELECT create_file_time FROM hr_payslip_run WHERE id = %s",[ids[0]])  #FILE CREATION TIME
	create_time = cr.fetchone()[0] 
#	raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(create_time))	
#	date_from = time.strftime('%Y/%m/%d')
#	times = time.strftime('%H:%M:%S')
	cr.execute("SELECT COUNT (*) FROM ijarah_hr_employee_rel WHERE payslip_id = %s",[ids[0]])
	count = cr.fetchone()[0]
	counts = count + 2
	cr.execute("SELECT ref_no FROM hr_payslip_run WHERE id = %s",[ids[0]])
	ref_no = cr.fetchone()[0]
#	raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(counts))	
        return [_(u'IFH'),
                _(u'IFILE'),
                _(u'CSV'),
                _(u'ABC32634001'),
                _(u'SASABBGSA003175114'),
		ref_no,		# File REfernce Number
		create_date,	# Creation Date of file
		create_time,	# Creation DAte of File
                _(u'P'),	
		_(u'1'),
		counts,		#Number of sales commission lines ''+ 2''		
                ]
############################################### Second line of CSV File ########################################################################
    def _get_row1_hr(self, cr, uid, ids, context=None):
	cr.execute("SELECT COUNT (*) FROM ijarah_hr_employee_rel WHERE payslip_id = %s",[ids[0]]) # No of Payment made in File.
	count = cr.fetchone()[0]
	counts = count 
	cr.execute("SELECT value_date FROM hr_payslip_run WHERE id = %s",[ids[0]]) #Value date/ For DAte
	get_value_date = cr.fetchone()[0]
	pattern=re.compile("[^\w']") # Remove Regular Expression from charcter field e.g '-'
	c = pattern.sub(' ', get_value_date) 
	value_date = c.replace(" ", "") # Remove Remaining whitespace from above field
#	raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(counts))	
        return [_(u'BATHDR'),
                _(u'ACH-CR'),
		 counts, #Total No of payments		
                 _(''), # BLANK
                 _(''), # BLANK
                 _(''), #BLANK
		 _('S'), #PAyment Purpose (Did'nt receive any special code for Commission Character therefore i leave it empty)		
		 _(''), #Payment Narration Free text field
		 _(''), #BLANK 
		_(u'@1ST@'),
                value_date,
		 _(u'011411717003'), #Debit Account Number
		 _(u'SAR'), #SAR Currency
		 _(''), #Total Amount being Paid Optional Field
                 _(''), # BLANK
                 _(''), # BLANK
                 _(''), # BLANK
                 _(''), # BLANK
                 _(''), # BLANK
                 _(''), # BLANK
                 _(''), # Company Name
                 _(''), # MOL Established ID
                 _(''), # EMPLOYER ID
                 _(''), # BLANK
                 _(''), # BLANK
                 _(''), # BLANK
                 _(u'SALARY'), # Batch Reference
                ]

    def _get_rows_hr(self, cr, uid, ids,
            employee_range_ids,
            date_start,
            date_end,		
            context=None):
	this = self.browse(cr,uid,ids[0],context=context)
	#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(ids[0]))	
	#blank = my hardoced
        cr.execute("""SELECT %(secpty)s,hr_employee.iban_no,hr_payslip.employee_name,hr_employee.ijarah_emp_no,hr_employee.bank_bic,%(blank1)s,
			%(blank2)s,cast(hr_payslip_line.total_amount as integer),%(blank3)s,%(blank4)s,%(blank5)s,%(blank6)s,%(blank7)s,
			%(blank8)s,%(n1)s,%(n2)s
			from hr_payslip,hr_payslip_run,ijarah_hr_employee_rel,hr_employee,hr_payslip_line 
			WHERE hr_payslip.state = 'done'
			AND ijarah_hr_employee_rel.payslip_id = hr_payslip_run.id
			AND hr_employee.id = hr_payslip.employee_id
			AND hr_payslip.id = hr_payslip_line.slip_id
			AND hr_payslip_line.code = 'NET' AND hr_payslip_line.name = 'Net'
			AND ijarah_hr_employee_rel.employee_id = hr_payslip.employee_id
			AND hr_payslip.payslip_run_id = hr_payslip_run.id  
			AND hr_payslip.date_from between hr_payslip_run.date_start AND hr_payslip_run.date_end
			AND ijarah_hr_employee_rel.employee_id in %(employee_id)s
			AND ijarah_hr_employee_rel.payslip_id = %(payslip_id)s
			ORDER by hr_payslip.id """,{'secpty':'SECPTY','blank1':'','blank2':'','blank3':'','blank4':'','blank5':'','blank6':'',
				'blank7':'','blank8':'','n1':'N','n2':'N','payslip_id': ids[0], 'employee_id':tuple(employee_range_ids)})

	res = cr.fetchall()

        rows = []
        for line in res:
            rows.append(list(line))
        return rows


    def get_data1(self, cr, uid, ids,result_type,context=None):
        get_header_func = getattr(self,("_get_header_%s"%(result_type)), None)
        get_row1_func = getattr(self,("_get_row1_%s"%(result_type)), None)
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
	
        rows = itertools.chain((get_header_func(cr, uid, ids, context=context),),(get_row1_func(cr, uid, ids, context=context),),
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
    	

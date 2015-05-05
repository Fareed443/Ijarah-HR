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
    _name = 'ijarah.sales.com.batch'
    _inherit = 'ijarah.sales.com.batch'
    _description = 'Export Text'

    _columns = {
        'file_name': fields.char('Export TxT', size=128),
	'data': fields.binary('Export TXT File',readonly=True),
        'company_id': fields.many2one('res.company', 'Company', invisible=True),
    }

    def _get_company_default(self, cr, uid, context=None):
        comp_obj = self.pool['res.company']
        return comp_obj._company_default_get(cr, uid, 'account.fiscalyear', context=context)


    _defaults = {'company_id': _get_company_default,
                 'file_name' : 'export_sales_commission_statement.txt',
	}

    def export_bank_statement(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        rows = self.get_data(cr, uid, ids, 'account', context)
        file_data = StringIO.StringIO()
        try:
            writer = AccountUnicodeWriter(file_data)
            writer.writerows(rows)
            file_value = file_data.getvalue()
            self.write(cr, uid, ids,
                       {'data': base64.encodestring(file_value)},
                       context=context)
        finally:
            file_data.close()

        return True

    def _get_header_account(self, cr, uid, ids, context=None):
	cr.execute("SELECT name FROM ijarah_sales_com_batch WHERE id = %s",[ids[0]]) #FILE CREATION DATE
	create_date = cr.fetchone()[0]
	cr.execute("SELECT create_file_time FROM ijarah_sales_com_batch WHERE id = %s",[ids[0]])  #FILE CREATION TIME
	create_time = cr.fetchone()[0] 
#	raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(create_time))	
#	date_from = time.strftime('%Y/%m/%d')
#	times = time.strftime('%H:%M:%S')
	cr.execute("SELECT COUNT (*) FROM ijarah_hr_emp_sales_com WHERE sales_com_run_id = %s",[ids[0]])
	count = cr.fetchone()[0]
	counts = count + 2
	cr.execute("SELECT ref_no FROM ijarah_sales_com_batch WHERE id = %s",[ids[0]])
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

    def _get_header2_account(self, cr, uid, ids, context=None):

	cr.execute("SELECT COUNT (*) FROM ijarah_hr_emp_sales_com WHERE sales_com_run_id = %s",[ids[0]]) # No of Payment made in File.
	count = cr.fetchone()[0]
	counts = count 
	cr.execute("SELECT date FROM ijarah_sales_com_batch WHERE id = %s",[ids[0]]) #Value date/ For DAte
	get_value_date = cr.fetchone()[0]
	pattern=re.compile("[^\w']") # Remove Regular Expression from charcter field e.g '-'
	c = pattern.sub(' ', get_value_date) 
	value_date = c.replace(" ", "") # Remove Remaining whitespace from above field
	cr.execute("SELECT ref_no FROM ijarah_sales_com_batch WHERE id = %s",[ids[0]])
	ref_no = cr.fetchone()[0]
#	raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(counts))	
        return [_(u'BATHDR'),
                _(u'ACH-CR'),
		 counts, #Total No of payments		
                 _(''), # BLANK
                 _(''), # BLANK
                 _(''), #BLANK
		 _(''), #PAyment Purpose (Did'nt receive any special code for Commission Character therefore i leave it empty)		
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
                 _(u'Commission'), # Batch Reference
                ]


    def _get_rows_account(self, cr, uid, ids,
            sales_com_ids,
            date,
            context=None):
	this = self.browse(cr,uid,ids[0],context=context)
	#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(ids[0]))	

	cr.execute("""SELECT %s,hr_employee.iban_no,hr_employee.name_related,hr_employee.emp_no,hr_employee.bank_bic,%s,%s,
			cast(ijarah_hr_emp_sales_com.amount as integer),%s,%s,%s,%s,%s,%s,%s,%s
			FROM ijarah_hr_emp_sales_com,hr_employee,ijarah_sales_com_batch
			WHERE ijarah_hr_emp_sales_com.sales_com_run_id = %s
			AND ijarah_hr_emp_sales_com.state = 'Done'
			AND ijarah_hr_emp_sales_com.name = hr_employee.id
			AND ijarah_hr_emp_sales_com.sales_com_run_id = ijarah_sales_com_batch.id
			AND ijarah_hr_emp_sales_com.month between ijarah_sales_com_batch.date_from and ijarah_sales_com_batch.date_to 
			AND ijarah_sales_com_batch.id = %s """,['SECPTY','','','','','','','','','N','N',ids[0],ids[0]])

        res = cr.fetchall()
	#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(res))	
        rows = []
        for line in res:
            rows.append(list(line))
        return rows


    def get_data(self, cr, uid, ids,result_type,context=None):
        get_header_func = getattr(self,("_get_header_%s"%(result_type)), None)
        get_header2_func = getattr(self,("_get_header2_%s"%(result_type)), None)
        get_rows_func = getattr(self,("_get_rows_%s"%(result_type)), None)
	#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(get_rows_func))	
        form = self.browse(cr, uid, ids[0], context=context)
        from_date = form.date
#        user_obj = self.pool.get('res.users')
        if form.sales_com_ids:
            employee_range_ids = [x.id for x in form.sales_com_ids]
 #           from_date = [x.id for x in form.periods]
        else:
            p_obj = self.pool.get("ijarah.hr.emp.sales.com")
            employee_range_ids = p_obj.search(cr, uid, [('month','=',from_date)], context=context)
	
        rows = itertools.chain((get_header_func(cr, uid, ids, context=context),),(get_header2_func(cr, uid, ids, context=context),),
                               get_rows_func(cr, uid, ids,employee_range_ids,					
                                             from_date,
                                             context=context)
                               )
	'''        
	rows = itertools.chain((get_header_func(cr, uid, ids, context=context),),
		get_rows_func(cr, uid, ids,employee_range_ids,from_date,context=context))
	'''
	return rows

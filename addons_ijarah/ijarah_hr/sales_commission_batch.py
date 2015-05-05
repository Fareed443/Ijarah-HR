from openerp.osv import osv, fields
from datetime import datetime,time
from openerp.addons import jasper_reports
from lxml import etree    
import datetime
import time
import math
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from datetime import timedelta
from dateutil import relativedelta
from datetime import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

class ijarah_sales_com_batch(osv.osv):

	_name = "ijarah.sales.com.batch"
	_columns = {
		'name':fields.char("File Creation Date",size=10),
		'desc':fields.char("Description",states={'Confirmed':[('readonly',True)]}), 
		'date':fields.date("For Date",states={'Confirmed':[('readonly',True)]}),
		'form_status':fields.boolean('Active',states={'Confirmed':[('readonly',True)]}),
		'state': fields.selection([('Draft', 'Draft'),('Confirmed', 'Confirmed')],'Status',  readonly=True,), 
		'ref_no':fields.char("Reference #",readonly=True),
		'create_file_time':fields.char("Create Time"),
		'create_file_date':fields.date("Create Date"),
	        'sales_com_ids': fields.one2many('ijarah.hr.emp.sales.com', 'sales_com_run_id', 'Sales Commission ID'),
		'date_from':fields.date("From Date",required=True),
		'date_to':fields.date("To Date",required=True),
	}
	_defaults={
		'form_status':True,
		'state':'Draft',
		'desc':lambda *a: ('Commission Slip for %s') %(time.strftime('%m-%Y')),
		'name':lambda *a: time.strftime('%Y/%m/%d'),
		'create_file_date':lambda *a: time.strftime('%Y-%m-%d'),
		'create_file_time':lambda *a: time.strftime('%H:%M:%S'),
		'date_from': lambda *a: time.strftime('%Y-%m-01'),
		'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],

#		'ref_no':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'ijarah.sales.com.batch'),
		}
	# Value Date/ For Data should be greater than or equal to creation date  not less than !!!!!!!!!!!!!!!!!!!!!!!!!!1
	def onchange_date(self, cr, uid,ids,date,create_file_date,context=None):
			today_date = time.strftime('%Y-%m-%d'),	
			for_date = date 
			if for_date < create_file_date:
				return { 'Warning':{'title':'warning','message':'The Date should not be less than today date'},'value' :{'date': ''}}
			return True
			#raise osv.except_osv(_('Error!'),_('For Date should not be less than today date and Creation date!'))
		
	def delete_state(self, cr, uid, ids, context=None):
		sale_com_id = self.pool.get('ijarah.hr.emp.sales.com')
		for x in self.browse(cr, uid, ids, context=context):
		    #delete imported Data
		    old_sales_com_id = sale_com_id.search(cr, uid, [('sales_com_run_id', '=', x.id)], context=context)
	#            old_sales_com_id
		    if old_sales_com_id:
		        sale_com_id.unlink(cr, uid, old_sales_com_id, context=context)
		    else:
			return True
#		self.unlink(cr, uid, ids,context=None)
		return super(ijarah_sales_com_batch, self).unlink(cr, uid, ids, context=context)
	
	def unlink(self, cr, uid, ids, context=None):
		self.delete_state(cr,uid,ids,context)
		bonus = self.pool.get('ijarah.sales.com.batch').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in bonus:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Entries which are already Confirmed!'))
#		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
#		return True
		return super(ijarah_sales_com_batch, self).unlink(cr, uid, ids, context=context)
    		
	def valid_state(self, cr, uid, ids, context=None):
	    next_seq = self.pool.get('ir.sequence').get(cr, uid, 'ijarah.sales.com.batch')
            for gp in self.browse(cr, uid, ids, context=context):
                if gp.sales_com_ids:        
 #                    cr.execute("DELETE FROM ijarah_hr_emp_sales_com WHERE sales_com_run_id = %s",(ids[0],))
			cr.execute('''UPDATE ijarah_hr_emp_sales_com 
			SET month = (SELECT ijarah_sales_com_batch.date FROM ijarah_sales_com_batch WHERE id = %s),
			state = 'Done',
			paid = 'True'			
			WHERE ijarah_hr_emp_sales_com.sales_com_run_id = %s ''',(ids[0],ids[0]))

			self.write(cr, uid, ids, {'state':'Confirmed','ref_no':next_seq}, context=context)
			self.export_bank_statement(cr,uid,ids,context)     # Generate Bank Statement		
			return True
	
ijarah_sales_com_batch()

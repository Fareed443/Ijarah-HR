from openerp.osv import osv, fields

class ijarah_visa_type(osv.osv):
	
	_name = "ijarah.visa.type"
	_columns = {
		'name'	: fields.char("Name",required=True),
	}	        	
ijarah_visa_type()

from openerp.osv import osv, fields

class ijarah_product(osv.osv):
	
	_name = "ijarah.product"
	_columns = {
		'name'	: fields.char("Name",required=True),
	}	        	
ijarah_product()

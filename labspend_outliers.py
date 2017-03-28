import psycopg2
import psycopg2.extras
import numpy as np
from scipy import stats
from operator import itemgetter

def find_outliers(sku, size, sku_by_size, outlier):
	a = []
	# outliers = {
	# 	'z_score': [],
	# 	'invoice_number': [],
	# 	'price': [],
	# 	'item_sku': [],
	# 	'size': []
	# }
	for item in sku_by_size:
		a.append(item[1])
	a = np.array(a)
	i = 0
	for z in stats.zscore(a):
		if z > 1.96 or z < -1.96:
			outlier.append([abs(z), sku_by_size[i][0], sku_by_size[i][1], sku, size])
			# outliers['z_score'].append(z)
			# outliers['invoice_number'].append(sku_by_size[i][0])
			# outliers['price'].append(sku_by_size[i][1])
			# outliers['item_sku'].append(sku)
			# outliers['size'].append(size)
		i = i + 1
	


conn = psycopg2.connect("dbname=labspend user=Saul1")

cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

cur.execute('SELECT invoice_number, item_sku, size, unit_price FROM invoices')

db_invoices = cur.fetchall()

skus = {
	'sizes': {
		'price': []
	}
}


for invoice in db_invoices:
	if not invoice['item_sku'].startswith("MISC"):
		if not invoice['item_sku'] in skus:
			skus[invoice['item_sku']] = skus.get(invoice['item_sku'], {})
		if not invoice['size'] in skus[invoice['item_sku']]:
			skus[invoice['item_sku']][invoice['size']] = skus[invoice['item_sku']].get(invoice['size'], [])
		price = invoice['unit_price'].replace(',','')
		if not float(price.strip('$')) <= 0:
			skus[invoice['item_sku']][invoice['size']].append([invoice['invoice_number'], float(price.strip('$'))])

outlier = []
for sku in skus:
	for size in skus[sku]:
		if len(skus[sku][size]) > 3:
			find_outliers(sku, size, skus[sku][size], outlier)
outlier.sort(key=itemgetter(0), reverse=True)

print ("OUTLIERS: \n")
i = 0
for i in range(100):
	print ("%d. invoice_number: %s 	price: %s 	item_sku: %s 	size: %s 	z-score: %s" % (i+1, outlier[i][1], outlier[i][2], outlier[i][3], outlier[i][4], outlier[i][0]))
	





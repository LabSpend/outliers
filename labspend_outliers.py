import psycopg2
import psycopg2.extras
import numpy as np
from scipy import stats
from operator import itemgetter
import getopt
import sys

def find_outliers_for_item(sku, size, sku_by_size, outlier):
	a = []

	#Add the item prices to the array
	for item in sku_by_size:
		a.append(item[1])

	#Turn a into an np array to run the zscore function
	a = np.array(a)
	#Keep track of i to access the information in sku_by_size
	i = 0


	for z in stats.zscore(a):
		#Only add outliers that you would expect to happen less than or equal to 5% of the time
		if z >= 1.96 or z <= -1.96:
			outlier.append([abs(z), sku_by_size[i][0], sku_by_size[i][1], sku, size])
		i = i + 1
	

def outlier_finder(database, username, password):

	#Connect to the database
	conn = psycopg2.connect("dbname=%s user=%s password=%s" % (database, username, password))
	cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

	#Pull the necessary data from the database
	cur.execute('SELECT invoice_number, item_sku, size, unit_price FROM invoices')
	db_invoices = cur.fetchall()

	#Create the skus dictionary to partition the data by sku and by size
	skus = {
		'sizes': {
			'price': []
		}
	}

	#Loop through the invoice data and add it to the sku database
	for invoice in db_invoices:

		#Don't include miscellaneous items in the outliers because this is a wide range of items
		if not invoice['item_sku'].startswith("MISC"):

			#Add sku to skus dictionary if not there already
			if not invoice['item_sku'] in skus:
				skus[invoice['item_sku']] = skus.get(invoice['item_sku'], {})

			#Add size for this specific sku if not in that dictionary already
			if not invoice['size'] in skus[invoice['item_sku']]:
				skus[invoice['item_sku']][invoice['size']] = skus[invoice['item_sku']].get(invoice['size'], [])
			#Change price to a float from a string and remove all free items (that were probably samples)
			price = invoice['unit_price'].replace(',','')
			if not float(price.strip('$')) == 0:
				#If it was not free add it to the price array in the sku size
				skus[invoice['item_sku']][invoice['size']].append([invoice['invoice_number'], float(price.strip('$'))])

	outlier = []

	#Loop through each sku in skus dictionary
	for sku in skus:

		#Loop through the different sizes in each sku
		for size in skus[sku]:

			#If the length of the price array is greater than 3 run the code to find outliers
			if len(skus[sku][size]) > 3:
				find_outliers_for_item(sku, size, skus[sku][size], outlier)

	#Sort the outliers by the magnitude of their z-score
	outlier.sort(key=itemgetter(0), reverse=True)

	#Print out the top 100 outliers with the invoice number, price, sku, size and the z-score
	print ("OUTLIERS: \n")
	for i in range(100):
		print ("%d. invoice_number: %s 	price: %s 	item_sku: %s 	size: %s 	z-score: %s" % (i+1, outlier[i][1], outlier[i][2], outlier[i][3], outlier[i][4], outlier[i][0]))
	


if __name__ == "__main__":
	password = ''
	database = ''
	username = ''

	#Command line arguments for the database, username, and password
	opts, args = getopt.getopt(sys.argv[1:], 'd:u:p', ["database=", "username=","password"])
	for opt, arg in opts:
		if opt in ("-d", "--database"):
			database = arg
		elif opt in ("-u", "--username"):
			username = arg
		elif opt in ("-p", "--password"):
			password = arg
		else:
			print ("Unhandled option")

	#Check that the user gave a database name
	if database == '':
		print ("Need database parameter")
		sys.exit(1)

	#Check that the user gave a username
	if username == '':
		print ("Need username parameter")
		sys.exit(1)

	#Find the outliers
	outlier_finder(database, username, password)



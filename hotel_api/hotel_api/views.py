from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_exempt

import requests
from datetime import timedelta 
from datetime import datetime as dttime
from .forms import *
from search.models import *


def hotels(request):
	form = HotelSearchForm()
	searches = Search.objects.all().order_by('-frequency')[:8]
	searches = [[item.keyword, item.image, float(item.lowest_price), int(item.lowest_points)/1000, item.keyword.split('-')[0]] for item in searches]

	if len(searches) < 8:
		searches += default_search

	return render(request, 'hotel_home.html', {'form': form, 'searches': searches})


HOTEL_CHAINS = {
	'ihg': 'IHG Rewards Club', 
	'spg': 'Starwood Preferred Guest', 
	'hh': 'Hilton HHonors', 
	'cp': 'Choice Privileges', 
	'cc': 'Club Carlson', 
	'mr': 'Marriott Rewards', 
	'hy': 'Hyatt Gold Passport', 
	'ac': 'Le Club Accor', 
	'wy': 'Wyndham Rewards',
}

def search_hotel(request):
	if request.method == 'POST':
		form = HotelSearchForm(request.POST)
		if form.is_valid():
			place = form.cleaned_data['place']
			checkin = form.cleaned_data['checkin']
			checkout = form.cleaned_data['checkout']
	else:
		place = request.GET.get('place')
		print place, '@@@@@'
		place = parse_place(place)
		print place, '########'
		checkin = request.GET.get('checkin') or dttime.today().strftime('%Y-%m-%d')
		checkout = request.GET.get('checkout') or (dttime.today() + timedelta(days=2)).strftime('%Y-%m-%d')
		form = HotelSearchForm(initial={'place':place, 'checkin': checkin, 'checkout': checkout})

	checkin_date = dttime.strptime(checkin, "%Y-%m-%d").date()
	checkout_date = dttime.strptime(checkout, "%Y-%m-%d").date()
	hotels = []

	if checkin_date < dttime.today().date() or checkout_date < dttime.today().date() or checkin_date > checkout_date:
		form.errors['Error: '] = 'Checkin date or checkout date is not correct. Please set it properly.'
	else:
		url = 'http://wandr.me/scripts/hustle/pex.ashx?term=%s&i=%s&o=%s' % (place, checkin, checkout)
		print url, '@@@@@@@@@@@@'
		try:
			res = requests.get(url=url).json()
			if res['results'] != 'error':
				hotels = res['hotels']
		except Exception, e:
			pass
	
	r_hotels = []

	print len(hotels), '@@@@@@@@@@@@'
	# save search
	if hotels:
		search = Search.objects.filter(keyword=place.strip())
		if search:
			search = search[0]
		else:
			search = Search()
			search.keyword = place.strip()

		search.frequency = search.frequency + 1
		search.image = get_image(hotels)
		search.lowest_price = get_lowest_price(hotels)
		search.lowest_points = get_lowest_points(hotels) 
		search.save()

	price_lowest = get_lowest_price(hotels)
	price_highest = get_highest_price(hotels)
	award_lowest = get_lowest_points(hotels)
	award_highest = get_highest_points(hotels)

	price_low = float(request.POST.get('price_low') or price_lowest)
	price_high = float(request.POST.get('price_high') or price_highest)
	award_low = int(request.POST.get('award_low') or award_lowest)
	award_high = int(request.POST.get('award_high') or award_highest)	
	radius = int(request.POST.get('radius') or 1000)	
	chain = request.POST.get('chain') or ''
	chain = get_chain(chain)
	dis_place = place.split('-')[0]
	print dis_place, '@@@@@@@@@'
	filters = [price_low, price_high, award_low, award_high, radius, chain, price_lowest, price_highest, award_lowest, award_highest, dis_place]

	# build price matrix
	price_matrix = {}
	for item in HOTEL_CHAINS:
		price_matrix[item] = {'cashRate': 100000000, 'pointsRate': 100000000, 'title': HOTEL_CHAINS[item]}

	# filter the hotels
	for hotel in hotels:
		cashRate = get_cash(hotel['cashRate'])
		pointsRate = get_points(hotel['pointsRate'])
		hradius = float(hotel['distance'] or 0)
		hchain = hotel['propID'].split('-')[0].strip()

		if cashRate and cashRate < price_low or cashRate > price_high:
			continue
		if pointsRate and pointsRate < award_low or pointsRate > award_high:
			continue
		if hradius > radius:
			continue
		if not hchain in chain:
			continue

		r_hotels.append(hotel)

		if cashRate and price_matrix[hchain]['cashRate'] > cashRate:
			price_matrix[hchain]['cashRate'] = cashRate

		if pointsRate and price_matrix[hchain]['pointsRate'] > pointsRate:
			price_matrix[hchain]['pointsRate'] = pointsRate

	return render(request, 'hotel_result.html', {'hotels': r_hotels[:3], 'form': form, 'price_matrix': price_matrix, 'filters': filters})

# used for initial bootstrap 
default_search = [
	['syd', 'http://cache.marriott.com/propertyimages/p/parsc/parsce01.jpg', 89.09, '5'],
	['sfo', 'http://cache.marriott.com/propertyimages/p/parsc/parsce01.jpg', 234.09, '2'],
	['cgd', 'http://cache.marriott.com/propertyimages/p/parsc/parsce01.jpg', 82.09, '4'],
	['cdg', 'http://cache.marriott.com/propertyimages/p/parsc/parsce01.jpg', 52.09, '6'],
	['hkg', 'http://cache.marriott.com/propertyimages/p/parsc/parsce01.jpg', 625.09, '2'],
	['syd', 'http://cache.marriott.com/propertyimages/p/parsc/parsce01.jpg', 234.09, '5'],
	['syd', 'http://cache.marriott.com/propertyimages/p/parsc/parsce01.jpg', 89.09, '5'],
	['syd', 'http://cache.marriott.com/propertyimages/p/parsc/parsce01.jpg', 89.09, '5'],
]

def get_cash(str_cash):
	'''
	get float cash value from the cash string
	return 0 if N/A
	'''
	str_cash = str_cash.replace('*', ' ') 
	str_cash = str_cash.strip()

	if str_cash == 'N/A':
		return 0
	else:
		return float(str_cash)

def get_points(str_points):
	'''
	get int points value from the points string
	return 0 if N/A
	'''
	str_points = str_points.replace(',', '')
	str_points = str_points.strip()

	if str_points == 'N/A':
		return 0
	else:
		return int(str_points)

def get_chain(serialize_str):
	'''
	get chains from the filter
	'''
	serialize_str = serialize_str.strip()
	if not serialize_str:
		return HOTEL_CHAINS.keys()

	serialize_str = serialize_str.replace('&', '')
	return serialize_str.split('hotel_chain=')

def get_image(hotels):
	'''
	get a valid image url from hotel list
	'''
	for hotel in hotels:
		if hotel['img'] != '':
			return hotel['img']

def get_lowest_price(hotels):
	'''
	get the lowest price from hotel list
	'''
	lowest = 100
	for hotel in hotels:
		cash = get_cash(hotel['cashRate'])
		if cash and lowest > cash:
			lowest = cash
	return lowest

def get_lowest_points(hotels):
	'''
	get the lowest points from hotel list
	'''
	lowest = 20000
	for hotel in hotels:
		points = get_points(hotel['pointsRate'])
		if points and lowest > points:
			lowest = points
	return lowest


def get_highest_price(hotels):
	'''
	get the highest price from hotel list
	'''
	highest = 100
	for hotel in hotels:
		cash = get_cash(hotel['cashRate'])
		if cash and highest < cash:
			highest = cash
	return highest

def get_highest_points(hotels):
	'''
	get the highest points from hotel list
	'''
	highest = 50000
	for hotel in hotels:
		points = get_points(hotel['pointsRate'])
		if points and highest < points:
			highest = points
	return highest

def parse_place(pre_place):
	'''
	get real place from encoded place string on twitter
	'''
	place = pre_place.replace('_', ' ')
	place = place.replace('0', ',')
	place = place.replace('1', ')')
	return place
'''
For only US hotels - it has limitation

API_KEY = 'GniPib2v9mca6jTnsJS4QvQ3Zf2CKHrVM86HCbQ3'
select = 'name,latitude,longitude,stars,highest_price,lowest_price'
url = 'https://api.factual.com/t/hotels-us?filters={"$and":[{"locality":{"$eq":"%s"}}]}&KEY=%s&select=%s' % (place, API_KEY, select)
hotels = requests.get(url=url).json()['response']['data']
if hotels != []:
	return render(request, 'hotel_result.html', {'hotels': hotels})	
'''

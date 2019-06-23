from bs4 import BeautifulSoup
import requests

BASE_URL = 'https://www.imdb.com/search/title/?groups=top_1000'

random_links_to_ignore = {
	'',
	'1',
	'2',
	'3',
	'4',
	'5',
	'6',
	'7',
	'8',
	'9',
	'10',
	'X',
	'Next »',
	'« Previous'
}

pages = []
i = 1
while i < 1000:
	if i == 1:
		pages.append('')
	else:
		pages.append(f"&start={i}")
	i += 50

movies = {}

# populate movies (movie name to list of relevant people)
print('\nScraping data\n')
for page in pages:
	url = BASE_URL + page
	print(f"Hitting: {url}")
	response = requests.get(url)
	html_doc = response.text
	dom = BeautifulSoup(html_doc, 'html.parser')

	links = dom.find(id='main').find_all('a')

	movie_name = None
	for link in links:
		txt = link.text.strip()
		if link.parent.name == 'h3':
			movie_name = txt
			movies[movie_name] = []
		elif movie_name and txt not in random_links_to_ignore:
			movies[movie_name].append(txt)

index = {}

# populate index (monolithic dictionary of any related keyword
# [parts of a movie name, actor, director, etc.] to full movie name)

# ideally we persist this in a key-value store such as redis
for movie_name in movies:
	keywords = movie_name.split()
	for person in movies[movie_name]:
		keywords += person.split()
	for keyword in keywords:
		keyword = keyword.lower()
		if keyword not in index:
			index[keyword] = set()
		index[keyword].add(movie_name)

keywords = input('\nPlease enter a space separated list of keywords related to your movie: ')
keywords = keywords.split()

relevant_movies = []
for keyword in keywords:
	keyword = keyword.lower()
	if keyword in index:
		relevant_movies.append(index[keyword])

relevant_movies_against_all_keywords = set.intersection(*relevant_movies) if relevant_movies else set()

if relevant_movies_against_all_keywords:
	print("\nWe've found the following movies relevant to your search:")
	for movie in relevant_movies_against_all_keywords:
		print(f"-{movie}")
else:
	print('\nNo relevant movies found')
print('')

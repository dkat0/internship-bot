"""
/*******************************************************************************
 * Data Structures Post-AP - Mr. Perez
 *
 * Name: Daniel Kathein
 * Period: 7
 *
 * Description: This tool, Internship Bot, helps students find internships in
 * fields and geographical locations of their choice. It is built off a
 * web-scraping system using the requests and BeautifulSoup libraries, which
 * scrapes Chegg Internships (internships.com) for recent postings. Users can
 * select the field and geographical location they want to search for internships
 * in.
 *
 *******************************************************************************/
"""

import requests
import bs4
import time
import webbrowser

class Internship:
    def __init__(self, soup):
        self.link = "https://www.internships.com" + soup.get('href')
        self.date_posted = soup.find('div', class_='col-3 days').find('span').text.strip()

        data = soup.find('div', class_='col-11 col-sm-10 desc')
        self.title = data.find('h4').text.strip()
        self.company, self.location = data.find('h5').text.split(' | ')
        self.brief_description = data.find('p', class_='description').text.strip()

        attributes = soup.find('div', class_='col-12 row pills').findAll('li')
        self.attributes = [a.text.strip() for a in attributes]

class InternshipBot:
    categories = {}
    locations = {}

    def run(self):
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print("Welcome to Internship Bot!")
        print("This tool helps students find internships in fields and geographical locations of their choice.")
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        time.sleep(1)
        input("Press set this window to FULL SCREEN and then press ENTER to continue.")

        self.get_sitemap_info()
        while True:
            field, location = self.user_selection()
            link_to_scrape = self.generate_link(field[1], location[1])

            self.search_internships(link_to_scrape)

    def search_internships(self, link):
        print("\nSearching...")
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }
        r = requests.get(link, headers=headers)
        soup = bs4.BeautifulSoup(r.text, 'lxml')

        average_pay = soup.find('div', class_='row salary-wrap').find('div', class_='salary').text
        page_title = soup.find('div', class_='col-9 col-md-12 content').find('h1').text.strip().split('Find 2022 ')[1]

        postings = soup.find('div', id='postings').findAll('a', class_='row posting')
        internships = [Internship(posting) for posting in postings]

        print("\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print(page_title)
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

        if len(internships) == 0:
            print("There are no available internships which match your criteria.")
            input("Press ENTER to update your field/location selection and search again.")
            return

        print(f"Selected {len(internships)} most recent postings.")
        print("Average Hourly Pay: " + average_pay + "\n")
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

        data = []
        for index, internship in enumerate(internships, start=1):
            data.append([f"[{index}]", f"{internship.title}", f"{internship.company}", f"{internship.location}"])

        # Code taken from online to print internships in a pretty column.
        widths = [max(map(len, col)) for col in zip(*data)]
        for row in data:
            print("  ".join((val.ljust(width) for val, width in zip(row, widths))))
        ################################################################

        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

        message = f"Please select an internship by its ID to learn more (1-{len(internships)}): "
        while True:
            selection = input(message)
            if selection.isdigit() and 0 < int(selection) <= len(internships):
                internship = internships[int(selection)-1]
                print("Opening internship link in your browser...\n")
                webbrowser.open(internship.link, new=2)

                message = f"Please select another internship by its ID to learn more (1-{len(internships)}), or type " \
                          f"'X' to update your field/location selection and search again: "
            elif selection.lower() == "x":
                return
            else:
                print(f"Invalid selection. Please enter a number from 1-{len(internships)} or type 'X' to search again.")

    def generate_link(self, field_id, location_id):
        if field_id is not None and location_id is not None:
            link = f"https://www.internships.com/{field_id}/{location_id}"
        elif field_id is not None:
            link = f"https://www.internships.com/{field_id}"
        elif location_id is not None:
            link = f"https://www.internships.com/{location_id}"
        return link

    def get_sitemap_info(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }
        r = requests.get("https://www.internships.com/sitemap", headers=headers)
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        categories_soup = soup.find('div', id='categories')

        for letter in categories_soup.findAll('ul'):
            entries = letter.findAll('li')[1:]
            for entry in entries:
                entry = entry.find('a')
                link = "https://www.internships.com" + entry.get('href')
                self.categories[entry.text] = link

        locations_soup = soup.find('div', id='locations')
        for state in locations_soup.findAll('ul'):
            if state.find('ul') is None:
                continue

            try:
                state_soup = state.find('li').find('a')
                state_name = state_soup.text
                state_link = "https://www.internships.com" + state_soup.get('href')
            except AttributeError:
                continue

            entries = state.find('ul').findAll('li')
            internship_entries = {}
            for entry in entries:
                entry = entry.find('a')
                link = "https://www.internships.com" + entry.get('href')
                internship_entries[entry.text] = link

            if internship_entries:
                self.locations[state_name] = [state_link, internship_entries]

    def user_selection(self):
        print("\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print("Field Selection")
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

        print("Options:")
        categories = list(self.categories.keys())
        categories_split = [categories[i:i+6] for i in range(0, len(categories), 6)]
        for c in categories_split:
            print(", ".join(c))
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

        field_choice = None
        field_link = None

        while True:
            field = input("What field would you like to search internships in (type 'all' for any)? ").strip()
            categories_lower = {k.lower():v for k, v in self.categories.items()}
            if field.lower() in categories_lower:
                field_choice = field
                field_link = categories_lower[field.lower()]
                break
            elif field.lower() == "all":
                break
            else:
                print("Invalid field. Please enter a valid field.")

        print("\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print("State Selection")
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        print("Options:")
        states = list(self.locations.keys())
        states_split = [states[i:i+6] for i in range(0, len(states), 6)]
        for s in states_split:
            print(", ".join(s))
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

        location_choice = None
        location_link = None

        while True:
            state = input("What state are you looking for internships around (type 'all' for any)? ").strip()
            locations_lower = {k.lower():v for k, v in self.locations.items()}
            if state.lower() in locations_lower:
                location_choice = state
                location_link, cities = locations_lower[state.lower()]
                break
            elif state.lower() == "all":
                cities = None
                break
            else:
                print("That state is not supported. Please try another state.")

        if cities is not None:
            print("\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            print("City Selection")
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            print("Internships are available around: " + ", ".join(list(cities.keys())))
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            while True:
                city = input("Which of these cities are you looking for internships around (type 'all' for any)? ").strip()
                cities_lower = {k.lower():v for k, v in cities.items()}
                if city.lower() in cities_lower:
                    location_choice = city + ", " + location_choice
                    location_link = cities_lower[city.lower()]
                    break
                elif city.lower() == "all":
                    break
                else:
                    print("That city is not supported. Please try another city.")

        if location_choice is None and field_choice is None:
            print("\nPlease narrow down your search with either a field or location selection!")
            print("Starting over...")
            time.sleep(3)
            self.start_find()
            return

        field_id = field_link.strip('/').split('/')[-1]
        location_id = location_link.strip('/').split('/')[-1]

        return [[field_choice, field_id], [location_choice, location_id]]

bot = InternshipBot()
bot.run()




import argparse
import codecs
import csv
import datetime
import io
import itertools
import random
import sys
import time
from urllib.request import urlopen


class Volunteer(object):
    def age_at_date(self, date):
        diff = date - self.birthdate
        return int(diff.days / 365.25)
    
    def randomize(self):
        self.entry_id = unique_int()
        self.lastname = random_lastname()
        self.firstname = random_firstname()
        self.nickname = random_nickname()
        self.birthdate = random_date(datetime.date(1988, 1, 1), datetime.date(2003, 1, 1))
        is_minor = self.age_at_date(datetime.date(2019, 8, 20)) < 18
        self.street = random_street()
        self.postcode = random_postcode()
        self.town = random_town()
        self.emailaddr = random_emailaddr()
        self.cellphone = random_cellphone()
        self.job = random_job()
        self.tshirt_size = random_choice(('XS', 'S', 'M', 'L', 'XL'))
        self.other_merch = 'Hoodie'
        self.vegetarian = random_choice(('ja', 'nein'))
        self.over_18 = 'Ja' if not is_minor else 'Nein'
        self.department_whishes = '' if is_minor else multi_choice(3, ('Troubleshooter', 'Einlass', 'Merchandise', 'Bar', 'Stagehand', 'Camping'))
        self.department_whishes_minors = '' if not is_minor else multi_choice(3, ('Troubleshooter', 'Einlass', 'Merchandise', 'Camping'))
        #self.shift_whishes = '' if is_minor else multi_choice(4, ('Donnerstag Früh', 'Freitag Früh', 'Freitag Spät', 'Samstag Früh', 'Samstag Spät'))
        #self.shift_whishes_minors = '' if not is_minor else multi_choice(2, ('Donnerstag Früh', 'Freitag Früh', 'Samstag Früh'))
        self.shift_whishes = '' if is_minor else multi_choice(4, ('Donnerstag 13:30 - 20:00', 'Freitag 13:30 - 19:30', 'Freitag 19:00 - 02:00', 'Samstag 13:30 - 19:30', 'Samstag 19:00 - 02:00'))
        self.shift_whishes_minors = '' if not is_minor else multi_choice(2, ('Donnerstag 13:30 - 19:30', 'Freitag 13:30 - 19:30', 'Samstag 13:30 - 19:30'))
        self.shift_whishes_troubleshooters = multi_choice(2, ('Donnerstag 14:00 - 19:00 Uhr', 'Freitag 14:00 - 02:00 Uhr', 'Samstag 14:00 - 02:00 Uhr'))
        self.shift_whishes_stagehands = multi_choice(2, ('Freitag 12:00 - 20:00 Uhr', 'Samstag 08:30 - 12:00 Uhr', 'Samstag 14:00 - 15:30 Uhr', 'Sonntag 08:00 - 14:00 Uhr'))
        self.shift_whishes_camping = multi_choice(2, ('I', 'forgot', 'what', 'these', 'were'))
        self.created = random_datetime(datetime.datetime(2019, 7, 20), datetime.datetime(2019, 8, 20))


headers = [
    'Entry ID',                                       # 0
    'Anmeldung Crew Runde 3',
    'Schritt 1',
    'Pflichtfelder',
    'Name',
    'Vorname',                                        # 5
    'Spitzname',
    'Geburtsdatum',
    'Straße und Hausnummer',
    'PLZ',
    'Ort',                                            # 10
    'separator',
    'E-Mail',
    'E-Mail erneut eingeben',
    'E-Mail Adressen falsch',
    'Mobilnummer',                                    # 15
    'separator',
    'Beruf/Studiengang/Erlerntes/Talent',
    'T-Shirt Größe',
    'Möchtest du zusätzlich zum Helfer T-Shirt noch weiteren Merch kaufen? Wenn ja, welchen?',
    'Ernährst du dich vegan/vegetarisch?',            # 20
    'separator',
    'Hinweis auf mögliche Gefahren',
    'separator',
    'Einwilligungserklärung',
    'Erklärung',                                      # 25
    'separator',
    'Grundsätze des Festivals',
    'Hinweis Schritt 1',
    'separator',
    '...',                                            # 30
    'separator',
    'Schritt 2',
    'Während dem Festival',
    'Bist du zum Festivalstart 18 Jahre alt?',
    'Ü18 Hauptaufgabengebiet "Während dem Festival"', # 35
    'Mindestens 3 Bereiche',
    'U18 Hauptaufgabengebiet "Während dem Festival"',
    'Bitte wähle deine Wunsch-Schichten (Ü18)',
    '...',
    'Bitte wähle deine Wunsch-Schichten (U18)',       # 40
    'Bitte wähle deine Wunsch-Schichten (Troubleshooter)',
    'Bitte wähle deine Wunsch-Schichten (Stagehand)',
    'Bitte wähle deine Wunsch-Schichten (Camping)',
    'separator',
    'Submit restrction message',                      # 45
    'Created'
]


column_templates = [
    "{.entry_id}", # 0
    "Anmeldung Crew Runde 3",
    "",
    "",
    "{.lastname}",
    "{.firstname}", # 5
    "{.nickname}",
    "{.birthdate:%d.%m.%Y}",
    "{.street}",
    "{.postcode}",
    "{.town}", # 10
    "",
    "{.emailaddr}",
    "{.emailaddr}",
    "",
    "{.cellphone}", # 15
    "",
    "{.job}",
    "{.tshirt_size}",
    "{.other_merch}",
    "{.vegetarian}", # 20
    "",
    "1",
    "",
    "",
    "1", # 25
    "",
    "1",
    "",
    "",
    "", # 30
    "",
    "",
    "",
    "{.over_18}",
    "{.department_whishes}", # 35
    "",
    "{.department_whishes_minors}",
    "{.shift_whishes}",
    "",
    "{.shift_whishes_minors}", # 40
    "{.shift_whishes_troubleshooters}",
    "{.shift_whishes_stagehands}",
    "{.shift_whishes_camping}",
    "",
    "", # 45
    "{.created:%d. %B %Y %H:%M}"
]


_last_unique_int = 0
def unique_int():
    global _last_unique_int
    next_unique_int = _last_unique_int + random.randint(1, 4)
    _last_unique_int = next_unique_int
    return next_unique_int


def fixed(value):
    return value


_lastnames = [
    'Mayer', 'Meyer', 'Müller', 'Fischer', 'Schmidt', 'Bauer', 'Köhler'
]

def random_lastname():
    return random.choice(_lastnames)


_firstnames = [
    'Alexander', 'Alexandra', 'Amelie', 'Anna', 'Annegret', 'Anne-Marie',
    'Anton', 'Antonia',
    'Benedikt', 'Benjamin', 'Bernd', 'Bernhard', 'Bettina', 'Bianca',
    'Brigitte',
    'Carolin', 'Christian', 'Christiane', 'Christina', 'Christine',
    'Daniel', 'Daniela', 'David', 'Detlev', 'Diana', 'Doris',
    'Emil', 'Emilia',
    'Fabian', 'Ferdinand', 'Florian', 'Frank', 'Franz',
    'Georg', 'Gerhardt', 'Gregor',
    'Hans', 'Heinz', 'Horst',
    'Ian',
    'Jan', 'Jens', 'Joachim', 'Johanna', 'Johannes', 'Jonas', 'Julia',
    'Julian',
    'Karl', 'Karla', 'Katharina', 'Katrin', 'Kerstin',
    'Lennart', 'Lisa', 'Ludwig', 'Luipold',
    'Maria', 'Marian', 'Marie', 'Mareike', 'Martin', 'Michael', 'Michaela',
    'Natalie', 'Natascha',
    'Otto', 'Olga',
    'Peter', 'Petra', 'Philipp',
    'Quintus',
    'Rainer', 'Rebecca',
    'Samuel', 'Sören', 'Stefan', 'Stefanie', 'Stephan', 'Stephanie',
    'Thomas', 'Tim', 'Thorsten', 'Thorben',
    'Ulrich',
    'Vladimir',
    'Walter',
    'Yvonne'
]
def random_firstname():
    return random.choice(_firstnames)


def random_nickname():
    return ''


def random_date(mindate, maxdate):
    mindt = datetime.datetime.combine(mindate, datetime.time(0, 0, 0))
    maxdt = datetime.datetime.combine(maxdate, datetime.time(0, 0, 0))
    min_unix = int(mindt.timestamp())
    max_unix = int(maxdt.timestamp())
    rnd_unix = random.randint(min_unix, max_unix)
    rnd_dt = datetime.datetime.fromtimestamp(rnd_unix)
    rnd_date = rnd_dt.date()
    return rnd_date


def random_street():
    return 'Musterstr. 1'

def random_postcode():
    return '86150'

def random_town():
    return 'Augsburg'

def random_emailaddr():
    return 'sammaier@example.com'

def random_cellphone():
    return '0123 45678901'

def random_job():
    return 'Student'

def random_choice(values):
    return random.choice(values)

def multi_choice(n, values):
    return ', '.join(random.sample(values, n))

def random_datetime(mindt, maxdt):
    min_unix = int(mindt.timestamp())
    max_unix = int(maxdt.timestamp())
    rnd_unix = random.randint(min_unix, max_unix)
    rnd_dt = datetime.datetime.fromtimestamp(rnd_unix)
    return rnd_dt


class OutputDialect(csv.Dialect):
    delimiter = ';'


def generate_row():
    v = Volunteer()
    v.randomize()
    row = [ct.format(v) for ct in column_templates]
    return row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--lines', type=int, default=20)
    args = parser.parse_args()

    #_init_lastnames()
    #_init_firstnames()
    
    with open('output.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(headers)
        for _ in range(args.lines):
            writer.writerow(generate_row())

def _cleanup(name):
    return name.split('_')[0]
    
def _init_firstnames():
    global _firstnames
    url = r'https://petscan.wmflabs.org/?language=de&project=wikipedia&categories=M%25C3%25A4nnlicher_Vorname%0D%0AWeiblicher%20Vorname&depth=1&combination=union&format=csv&sortby=ns_title&doit='
    firstnames = _init_from_petscan_titles(url)
    _firstnames = firstnames

def _init_lastnames():
    global _lastnames
    url = r'https://petscan.wmflabs.org/?language=de&project=wikipedia&categories=Familienname&combination=union&ns%5B0%5D=1&sortby=ns_title&doit=&format=csv'
    lastnames = _init_from_petscan_titles(url)
    _lastnames = lastnames

def _init_from_petscan_titles(url):
    elements = []
    backup_time = 0.5
    while True:
        with urlopen(url) as f:
            print(dict(f.headers))
            f = io.BytesIO(f.read())
            f_dec = codecs.getreader('utf-8')(f)
            reader = csv.reader(f_dec, delimiter=',', quoting=csv.QUOTE_ALL, lineterminator='\n')
            for row in itertools.islice(reader, 1, None):
                elements.append(_cleanup(row[1]))
            if not elements:
                print("Warning: Got empty response from {}".format(url))
                sys.stdout.flush()
                time.sleep(backup_time)
                backup_time = backup_time * 2
                continue
            break
    return list(set(elements))

if __name__ == '__main__':
    main()

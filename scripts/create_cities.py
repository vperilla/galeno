from proteus import config, Model
import csv
import pdb
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def create_cities(host, port, database, username, password, filename):
    pdb.set_trace()
    config.set_xmlrpc('http://%s:%s@%s:%s/%s/'
        % (username, password, host, port, database))

    Subdivision = Model.get('country.subdivision')
    to_save = []
    Country = Model.get('country.country')
    ecuador, = Country.find([('code', '=', 'EC')])
    cities = Subdivision.find([('type', '=', 'city'), ('country', '=', ecuador.id)])
    Subdivision.delete(cities)

    with open(filename, 'rb') as group_file:
        fieldnames = ['parent', 'name', 'number']
        reader = csv.DictReader(
            group_file, delimiter=';', fieldnames=fieldnames)
        reader.next()  # Skip header
        for row in reader:
            city = Subdivision()
            parent, = Subdivision.find([('code', '=', row['parent'])])
            city.country = parent.country
            city.name = row['name']
            city.code = row['parent'] + row['number']
            city.parent = parent
            city.type = 'city'
            to_save.append(city)
        Subdivision.save(to_save)


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', dest='host',
        help='host', default='localhost')
    parser.add_argument('--port', dest='port',
        help='port', default='8000')
    parser.add_argument('--database', dest='database',
        help='database', required=True)
    parser.add_argument('--user', dest='user',
        help='user', required=True)
    parser.add_argument('--password', dest='password',
        help='password', required=True)
    parser.add_argument('--filename', dest='filename',
        help='filename', required=True)
    options = parser.parse_args()
    create_cities(options.host, options.port, options.database,
        options.user, options.password, options.filename)

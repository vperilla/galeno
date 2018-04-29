from proteus import config, Model
import csv
import pdb
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def create_categories(host, port, database, username, password, filename):
    pdb.set_trace()
    config.set_xmlrpc('http://%s:%s@%s:%s/%s/'
        % (username, password, host, port, database))

    Category = Model.get('galeno.disease.category')

    with open(filename, 'rb') as category_file:
        fieldnames = ['code', 'name', 'parent']
        reader = csv.DictReader(
            category_file, delimiter=';', fieldnames=fieldnames)
        reader.next()  # Skip header
        for row in reader:
            if row['parent'] != '':
                parent, = Category.find([('code', '=', row['parent'])])
            else:
                parent = None
            category = Category()
            category.code = row['code']
            category.name = row['name']
            category.parent = parent
            category.save()


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
    create_categories(options.host, options.port, options.database,
        options.user, options.password, options.filename)

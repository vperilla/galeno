from proteus import config, Model
import csv
import pdb
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def create_diseases(host, port, database, username, password, filename):
    pdb.set_trace()
    config.set_xmlrpc('http://%s:%s@%s:%s/%s/'
        % (username, password, host, port, database))

    Disease = Model.get('galeno.disease')
    Group = Model.get('galeno.disease.group')
    Category = Model.get('galeno.disease.category')
    to_save = []

    with open(filename, 'rb') as disease_file:
        fieldnames = ['code', 'name', 'category', 'groups', 'chromosome',
            'protein', 'gene', 'information', 'active']
        reader = csv.DictReader(
            disease_file, delimiter=';', fieldnames=fieldnames)
        reader.next()  # Skip header
        for row in reader:
            print(row)
            disease = Disease()
            for field in row:
                if row[field] == '':
                    value = None
                else:
                    if field == 'active':
                        value = bool(row[field])
                    elif field == 'category':
                        category, = Category.find([('code', '=', row[field])])
                        value = category
                    elif field == 'groups':
                        value = []
                        for group_code in row[field].split(','):
                            group, = Group.find([('code', '=', group_code)])
                            value.append(group)
                    else:
                        value = row[field]
                if field != 'groups':
                    setattr(disease, field, value)
                else:
                    if value:
                        for group in value:
                            disease.groups.append(group)
            to_save.append(disease)
        Disease.save(to_save)


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
    create_diseases(options.host, options.port, options.database,
        options.user, options.password, options.filename)

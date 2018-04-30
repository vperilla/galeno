from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from proteus import config, Model

from datetime import datetime
import csv


def create_medicaments(host, port, database, username, password, filename):

    import pdb; pdb.set_trace()

    config.set_xmlrpc('http://%s:%s@%s:%s/%s/'
        % (username, password, host, port, database))

    Medicament = Model.get('galeno.medicament')
    to_save = []

    with open(filename, 'rb') as disease_file:
        fieldnames = ['a', 'b', 'release_date', 'expiration_date',
            'e', 'f', 'g', 'laboratory', 'i', 'j', 'name', 'l', 'presentation',
            'n', 'o', 'type_', 'sale_kind', 'adm_route', 'code', 't',
            'composition', 'notes', 'w', 'x', 'y', 'z']
        reader = csv.DictReader(
            disease_file, delimiter='|', fieldnames=fieldnames)
        reader.next()  # Skip header
        for row in reader:
            if row['release_date'] != '':
                r_date = datetime.strptime(
                    row['release_date'], '%Y-%m-%d %H:%M:%S')
            else:
                r_date = None
            if row['expiration_date'] != '':
                e_date = datetime.strptime(
                    row['expiration_date'], '%Y-%m-%d %H:%M:%S')
            else:
                e_date = None

            print(row)
            medicament = Medicament()
            medicament.code = row['code'].decode('utf-8')
            medicament.name = row['name'].decode('utf-8')
            medicament.release_date = r_date
            medicament.expiration_date = e_date
            medicament.laboratory = row['laboratory'].decode('utf-8')
            medicament.presentation = row['presentation'].decode('utf-8')
            medicament.type_ = row['type_'].decode('utf-8')
            medicament.sale_kind = row['sale_kind'].decode('utf-8')
            medicament.administration_route = row['adm_route'].decode('utf-8')
            medicament.composition = row['composition'].decode('utf-8')
            medicament.notes = row['notes'].decode('utf-8')
            to_save.append(medicament)
        Medicament.save(to_save)


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', dest='host', default='localhost',
        help='localhost')
    parser.add_argument('--port', dest='port', default='8000',
        help='port')
    parser.add_argument('--database', dest='database', required=True,
        help='database')
    parser.add_argument('--user', dest='user', required=True,
        help='user name')
    parser.add_argument('--password', dest='password', required=True,
        help='password')
    parser.add_argument('--filename', dest='filename', required=True,
        help='filename')
    options = parser.parse_args()
    create_medicaments(options.host, options.port, options.database,
        options.user, options.password, options.filename)

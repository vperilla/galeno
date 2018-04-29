from proteus import config, Model
import csv
import pdb
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def create_diseases(host, port, database, username, password, filename):
    pdb.set_trace()
    config.set_xmlrpc('http://%s:%s@%s:%s/%s/'
        % (username, password, host, port, database))

    Disease = Model.get('galeno.disease')

    diseases = Disease.find([])
    with open(filename, 'wb') as disease_file:
        fieldnames = ['code', 'name', 'category', 'groups', 'chromosome',
            'protein', 'gene', 'information', 'active']
        writer = csv.DictWriter(
            disease_file, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        for disease in diseases:
            print(disease)
            groups = None
            for group in disease.groups:
                if groups is None:
                    groups = ""
                else:
                    groups += ','
                groups += group.code.encode('utf-8')
            writer.writerow({
                'code': disease.code.encode('utf-8'),
                'name': disease.name.encode('utf-8'),
                'category': disease.category.id,
                'gene': disease.gene and disease.gene.encode('utf-8') or None,
                'groups': groups,
                'information': disease.information
                and disease.information.encode('utf-8') or None,
                'chromosome': disease.chromosome
                and disease.chromosome.encode('utf-8') or None,
                'protein': disease.protein
                and disease.protein.encode('utf-8') or None,
                'active': disease.active,
            })


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

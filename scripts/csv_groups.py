from proteus import config, Model
import csv
import pdb
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def create_groups(host, port, database, username, password, filename):
    pdb.set_trace()
    config.set_xmlrpc('http://%s:%s@%s:%s/%s/'
        % (username, password, host, port, database))

    Group = Model.get('galeno.disease.group')

    groups = Group.find([])
    with open(filename, 'wb') as group_file:
        fieldnames = ['code', 'name', 'description', 'information']
        writer = csv.DictWriter(
            group_file, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        for group in groups:
            if group.description:
                description = group.description.encode('utf-8')
            else:
                description = None
            if group.information:
                information = group.information.encode('utf-8')
            else:
                information = None
            writer.writerow({
                'code': group.code.encode('utf-8'),
                'name': group.name.encode('utf-8'),
                'description': description,
                'information': information,
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
    create_groups(options.host, options.port, options.database,
        options.user, options.password, options.filename)

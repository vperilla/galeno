from genshi.template import TemplateLoader
import io
import csv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def create_city_xml(filename, template, result_filename):
    import pdb; pdb.set_trace()  # XXX BREAKPOINT
    loader = TemplateLoader(['templates'], auto_reload=True)
    template = loader.load(template)
    with open(filename, 'r') as city_file:
        fieldnames = ['code', 'name', 'type', 'parent', 'country']
        reader = csv.DictReader(
            city_file, delimiter=';', fieldnames=fieldnames)
        reader.next()  # Skip header
        cities = []
        for row in reader:
            cities.append({
                'number': row['code'].lower().decode('utf-8'),
                'code': row['code'].decode('utf-8'),
                'name': row['name'].decode('utf-8'),
                'type': row['type'].decode('utf-8'),
                'parent': row['parent'].decode('utf-8'),
                'country': row['country'].decode('utf-8'),
            })

    result_file = io.open(result_filename, 'w', encoding='utf-8')
    result_file.write(template.generate(cities=cities).render())
    result_file.close()


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--filename', dest='filename',
        help='filename', required=True)
    parser.add_argument('--template', dest='template',
        help='template', required=True)
    parser.add_argument('--result', dest='result',
        help='result file name', required=True)
    options = parser.parse_args()
    create_city_xml(options.filename, options.template, options.result)

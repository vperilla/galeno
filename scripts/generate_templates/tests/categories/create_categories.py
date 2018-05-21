from genshi.template import TemplateLoader
import io
import csv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def create_category_xml(filename, template, result_filename):
    import pdb; pdb.set_trace()  # XXX BREAKPOINT
    loader = TemplateLoader(['templates'], auto_reload=True)
    template = loader.load(template)
    with open(filename, 'r') as category_file:
        fieldnames = ['number', 'name']
        reader = csv.DictReader(
            category_file, delimiter=';', fieldnames=fieldnames)
        reader.next()  # Skip header
        categories = []
        for row in reader:
            categories.append({
                'number': row['number'].decode('utf-8'),
                'name': row['name'].decode('utf-8'),
            })

    result_file = io.open(result_filename, 'w', encoding='utf-8')
    result_file.write(template.generate(categories=categories).render())
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
    create_category_xml(options.filename, options.template, options.result)

from genshi.template import NewTextTemplate
import io
import csv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def create_vaccine_xml(filename, template, result_filename):
    import pdb; pdb.set_trace()  # XXX BREAKPOINT
    template_content = open(template, 'r')
    template = NewTextTemplate(template_content.read())
    with open(filename, 'r') as vaccine_file:
        fieldnames = ['number', 'name', 'description', 'name_es',
            'description_es']
        reader = csv.DictReader(
            vaccine_file, delimiter=';', fieldnames=fieldnames)
        reader.next()  # Skip header
        vaccines = []
        for row in reader:
            vaccines.append({
                'number': row['number'].decode('utf-8'),
                'name': row['name'].decode('utf-8'),
                'name_es': row['name_es'].decode('utf-8'),
                'description': row['description'].decode('utf-8'),
                'description_es': row['description_es'].decode('utf-8'),
            })

    result_file = io.open(result_filename, 'w', encoding='utf-8')
    result_file.write(template.generate(vaccines=vaccines).render())
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
    create_vaccine_xml(options.filename, options.template, options.result)

#!/usr/bin/env python
import sys
import csv
import codecs
import getopt

from selectolax.parser import HTMLParser

def main():
    input_path, output_path = read_args()
    sanitize_csv(input_path, output_path)

def sanitize_csv(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8', errors='cp1252fallback') as input_file:
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as output_file:
            input_csv = csv.reader(input_file)
            output_csv = csv.writer(output_file)

            for row_index, row in enumerate(input_csv):
                if row_index > 0:
                    sanitize_row(row)

                output_csv.writerow(row)

def sanitize_row(row):
    for cell_index, cell in enumerate(row):
        row[cell_index] = sanitize_cell(cell)

def sanitize_cell(cell):
    if '<' in cell:
        cell = remove_html_tags(cell)

    cell = fix_encoding(cell)

    return cell

def remove_html_tags(cell):
    tree = HTMLParser(cell)
    for tag in tree.css('script, style'):
        tag.decompose()

    text_content = tree.text(deep=True)

    return text_content

def fix_encoding(cell):
    fixed_cell = cell.encode('cp1252', errors='utf8fallback').decode('utf-8', errors='cp1252fallback')

    return fixed_cell

def read_args():
    input_path = None
    output_path = None

    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'i:o:h', ['input=', 'output=', 'help'])
    except getopt.GetoptError as error:
        print(error)
        print_usage()
        sys.exit(1)
    
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_usage()
            sys.exit()
        elif opt in ('-i', '--input'):
            input_path = arg
        elif opt in ('-o', '--output'):
            output_path = arg
    
    if not input_path or not output_path:
        print_usage()
        sys.exit(1)

    return (input_path, output_path)

def print_usage():
    print('Usage: csv-sanitizer.py [-i] [-o]')
    print('Required arguments:')
    print('-i, --input      Path of the input CSV file')
    print('-o, --output     Path for the sanitized CSV file')
    print()
    print('Optional arguments:')
    print('-h, --help       Show this help message and exit')

def utf8_fallback(codec_error):
    start = codec_error.start
    end = codec_error.end
    unencodable_chars = codec_error.object[start:end]

    return (unencodable_chars.encode('utf-8'), end)

def cp1252_fallback(codec_error):
    start = codec_error.start
    end = codec_error.end
    undecodable_chars = codec_error.object[start:end]

    return (undecodable_chars.decode('cp1252'), end)

codecs.register_error('utf8fallback', utf8_fallback)
codecs.register_error('cp1252fallback', cp1252_fallback)

if __name__ == '__main__':
    main()

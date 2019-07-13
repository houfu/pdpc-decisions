#  MIT License Copyright (c) 2019. Houfu Ang.
import argparse
import re
import sys


def remove_extra_linebreaks(source):
    return [x for x in source if x != '' or not re.search(r'^\s+$', x)]


def remove_numbers_as_first_characters(source):
    return [x for x in source if not re.search(r'^\d*[\s.]*$', x)]


def remove_citations(source):
    return [x for x in source if not re.search(r'^\[\d{4}]\s+(?:\d\s+)?[A-Z|()]+\s+\d+[\s.]?$', x)]


def remove_feed_carriage(source):
    return [x for x in source if not re.search(r'\f', x)]


def join_sentences_in_paragraph(source):
    result = []
    paragraph_string = ''
    for x in source:
        if re.search(r'\.\s*$', x):
            paragraph_string += x
            result.append(paragraph_string)
            paragraph_string = ''
        else:
            paragraph_string += x
    return result


# main

def clean_up_source(text):
    text_lines = text.split('\n')
    start_count = len(text_lines)
    text_lines = remove_extra_linebreaks(text_lines)
    text_lines = remove_numbers_as_first_characters(text_lines)
    text_lines = remove_citations(text_lines)
    text_lines = remove_feed_carriage(text_lines)
    text_lines = join_sentences_in_paragraph(text_lines)
    end_count = len(text_lines)
    print('Reduced from {0} lines to {1} lines. {2}% Wow'.format(start_count, end_count, end_count / start_count * 100))
    return '\n'.join(text_lines)


def make_the_parser():
    parser = argparse.ArgumentParser(description='Process some files by cleaning and clearing the text')
    parser.add_argument('source', help='Source file to process')
    parser.add_argument('-l', '--line-breaks', help='Stop cleaner from removing extra line breaks',
                        action='store_false')
    parser.add_argument('-n', '--numbers',
                        help='Stop cleaner from Removing numbers. Usually these are paragraph or page numbers.',
                        action='store_false')
    parser.add_argument('-c', '--citation',
                        help='Stop cleaner from removing citations in a new line. ' +
                             'Usually a page heading for the current case',
                        action='store_false')
    parser.add_argument('-f', '--feed_carriage',
                        help='Stop cleaner from removing anything with a feed carriage in the line ' +
                             'Usually a page heading for the current case',
                        action='store_false')
    parser.add_argument('-j', '--join_sentences',
                        help='Stop cleaner from trying to join sentences in a paragraph.' +
                             'If other flags are set to false, this may end with strange results',
                        action='store_false')
    parser.add_argument('-N', '--new-file', help='Instead of overwriting the source file, create a new file instead.')
    return parser


def main(args=None):
    parser = make_the_parser()
    options = parser.parse_args(args=args)

    with open(options.source) as fp:
        text_lines = fp.read().split('\n')
        start_count = len(text_lines)
        if options.line_breaks:
            text_lines = remove_extra_linebreaks(text_lines)
        if options.numbers:
            text_lines = remove_numbers_as_first_characters(text_lines)
        if options.citation:
            text_lines = remove_citations(text_lines)
        if options.feed_carriage:
            text_lines = remove_feed_carriage(text_lines)
        if options.join_sentences:
            text_lines = join_sentences_in_paragraph(text_lines)
        end_count = len(text_lines)
        print('Reduced from {0} lines to {1} lines'.format(start_count, end_count))
        fp.close()
        text = '\n'.join(text_lines)
        if options.new_file:
            newfile = open(options.new_file, 'w')
            newfile.write(text)
            newfile.close()
        else:
            overwritefile = open(options.source, 'w')
            overwritefile.write(text)
            overwritefile.close()


if __name__ == "__main__":
    # execute only if run as a script
    sys.exit(main())

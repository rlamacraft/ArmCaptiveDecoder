from jinja2 import Environment, FileSystemLoader

def prepend_lines(multiline_string, prefix):
    """prepend a string before every line i.e. after every newline char"""
    return(prefix + multiline_string.replace('\n', '\n' + prefix))

def generate_code(encodings_sets):
    env = Environment(
        loader=FileSystemLoader('.'),
        line_statement_prefix='#'
    )
    env.filters['prepend_lines'] = prepend_lines
    template = env.get_template('decoder.cpp.jinja')
    return(template.render(sets=encodings_sets))

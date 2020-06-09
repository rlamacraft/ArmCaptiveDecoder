from jinja2 import Environment, FileSystemLoader

def generate_code(encodings_sets):
    env = Environment(
        loader=FileSystemLoader('.'),
        line_statement_prefix='#'
    )
    template = env.get_template('decoder.cpp.jinja')
    return(template.render(sets=encodings_sets))

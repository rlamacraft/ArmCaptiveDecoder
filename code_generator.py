from jinja2 import Environment, FileSystemLoader

def prepend_lines(multiline_string, prefix):
    """prepend a string before every line i.e. after every newline char"""
    return(prefix + multiline_string.replace('\n', '\n' + prefix))

def environment():
    return(Environment(
        loader=FileSystemLoader('.'),
        line_statement_prefix='£'
    ))

def generate_code(encodings_sets, instructions):
    generate_decoder_h(instructions)
    generate_decoder_cpp(encodings_sets)

def generate_decoder_h(instructions):
    env = environment()
    template = env.get_template('templates/decoder.h.jinja')
    with open('out/decoder.h', 'w') as file:
        file.write(template.render(
            instructions=instructions
        ))
    print("Written to out/decoder.h")

def generate_decoder_cpp(encodings_sets):
    env = environment()
    template = env.get_template('templates/decoder.cpp.jinja')
    with open('out/decoder.cpp', 'w') as file:
        file.write(template.render(
            sets=encodings_sets,
            drop_unbound_from_pos_map=lambda pos_map: dict([(x,(y,z)) for x,(y,z) in pos_map.items() if z is not None]),
            list=list
        ))
    print("Written to out/decoder.cpp")

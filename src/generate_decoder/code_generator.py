from jinja2 import Environment, FileSystemLoader
import re

def prepend_lines(multiline_string, prefix):
    """prepend a string before every line i.e. after every newline char"""
    return(prefix + multiline_string.replace('\n', '\n' + prefix))

def mk_cpp_identifier(string):
    """Convert any passed string into a valid c++ identifier by converting all invalid chars to underscores"""
    return(re.sub(r"[^a-zA-Z0-9]","_",string))

def environment():
    return(Environment(
        loader=FileSystemLoader('../..'),
        line_statement_prefix='£'
    ))

def generate_code(encodings_sets, instructions):
    generate_decoder_h(instructions)
    generate_decode_h()
    generate_disasm_cpp(instructions)
    generate_decoder_cpp(encodings_sets)

def generate_decode_h():
    env = environment()
    template = env.get_template('templates/decode.h.jinja')
    with open('../../out/decode.h', 'w') as file:
        file.write(template.render(
        ))
    print("Written to out/decode.h")

def generate_disasm_cpp(instructions):
    env = environment()
    template = env.get_template('templates/disasm.cpp.jinja')
    with open('../../out/disasm.cpp', 'w') as file:
        file.write(template.render(
            instructions=instructions
        ))
    print("Written to out/disasm.cpp")

def generate_decoder_h(instructions):
    env = environment()
    template = env.get_template('templates/decoder.h.jinja')
    with open('../../out/arm64-decode.h', 'w') as file:
        file.write(template.render(
            instructions=instructions,
            mk_cpp_identifier=mk_cpp_identifier
        ))
    print("Written to out/decoder.h")

def generate_decoder_cpp(encodings_sets):
    env = environment()
    template = env.get_template('templates/decoder.cpp.jinja')
    with open('../../out/arm64-decode.cpp', 'w') as file:
        file.write(template.render(
            sets=encodings_sets,
            jumps={
                "op_aarch64_a64_b_uncond_b_only_branch_imm": { # b_uncond.xml
                    "type": "DIRECT",
                    "predicated": False,
                    "target": True,
                },
                "op_aarch64_a64_b_cond_b_only_condbranch": { # b_cond.xml
                    "type": "INDIRECT",
                    "predicated": False,
                    "target": False,
                    "is_predicated": True,
                },
                "op_aarch64_a64_br_br_64_branch_reg": { # br.xml
                    "type": "INDIRECT",
                    "predicated": False,
                    "target": False,
                },
                "op_aarch64_a64_cbz_br19": { # cbz.xml
                    "type": "DIRECT",
                    "predicated": True,
                    "target": True,
                },
                "op_aarch64_a64_drps_drps_64e_branch_reg": { # drps.xml
                    "type": "INDIRECT",
                    "predicated": False,
                    "target": False,
                },
                "op_aarch64_a64_eret_eret_64e_branch_reg": { # eret.xml
                    "type": "INDIRECT",
                    "predicated": False,
                    "target": False,
                },
                "op_aarch64_a64_ret_ret_64r_branch_reg": { # ret.xml
                    "type": "INDIRECT",
                    "predicated": False,
                    "target": False,
                },
                "op_aarch64_a64_tbz_tbz_only_testbranch": { # tbz.xml
                    "type": "DIRECT",
                    "predicated": True,
                    "target": False,
                }
            },
            drop_unbound_from_pos_map=lambda pos_map: dict([(x,(y,z)) for x,(y,z) in pos_map.items() if z is not None]),
            list=list,
            mk_cpp_identifier=mk_cpp_identifier
        ))
    print("Written to out/decoder.cpp")

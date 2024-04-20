"""
Parse SAD sequence to XSuite Line

Author(s):      Giovani Iadarola, John Salvesen
Forked:         20/04/2024
Last Edited:    20/04/2024
"""

################################################################################
# Python Setup
################################################################################

########################################
# Packages
########################################
import json

########################################
# User Arguments
########################################
fname = 'sler_1705_60_06_cw50_4b.plain.sad'
# fname = 'sler_1707_80_1_simple.sad'


################################################################################
# Read the SAD file
################################################################################
with open(f"lattices/{fname}", 'r', encoding="utf-8") as sad_file:
    content = sad_file.read()

content = content.lower() # make it lower case

########################################
# Correct Bad Formatting
########################################
while ' =' in content:
    content = content.replace(' =', '=')

while '= ' in content:
    content = content.replace('= ', '=')

while '  ' in content:
    content = content.replace('  ', ' ')

content = content.replace('deg', '')

########################################
# Split the SAD file into sections
########################################
sections = content.split(';')
out = {}
for ss in sections:
    ss_py = ss
    ss_py = ss_py.strip()

    # If the section is empty, skip
    if len(ss_py) == 0:
        continue

    ss_command = ss_py.split()[0]
    # Check is the command is a known command
    if ss_command in ('drift', 'bend', 'quad', 'oct', 'mult', 'sol', 'cavi',
                'mark', 'moni', 'beambeam', 'apert'):
        ss_py = ss_py.replace('(', 'dict(').replace(')', '),')
        ss_py = ss_py.replace(ss_command, 'dict(')
        lines = ss_py.split('\n')
        for il, ll in enumerate(lines):
            tokens = ll.split(' ')
            for it, tt in enumerate(tokens):
                if '=' in tt:
                    tokens[it] = tt + ','
            lines[il] = ' '.join(tokens)
        ss_py = '\n'.join(lines)
        ss_py ='dict(\n' + ss_py + '\n)'
        while ',,' in ss_py:
            ss_py = ss_py.replace(',,', ',')

        ss_py += ')'

        dct = eval(ss_py)
        if ss_command in out:
            out[ss_command].update(dct)
        else:
            out[ss_command] = dct

    if ss_command == 'line':
        ele_str = ss.split('=')[-1]
        ele_str = ele_str.replace('(', '')
        ele_str = ele_str.replace(')', '')
        ele_str.replace('\n', ' ')
        ele_str_list = []
        for ee in ele_str.split():
            if len(ee) > 0:
                ele_str_list.append(ee)

        out['line'] = ele_str_list

################################################################################
# Save as a JSON
################################################################################
out_file_name = 'lattices/' + fname.replace('.plain.sad', '') + '.json'
with open(out_file_name, 'w', encoding="utf-8") as out_file:
    json.dump(out, out_file, indent=2)

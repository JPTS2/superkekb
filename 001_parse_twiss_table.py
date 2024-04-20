"""
Parse SAD Twiss Table to Python

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
from io import StringIO
import json
import pandas as pd
import xobjects as xo

########################################
# User Arguments
########################################
fname = 'sler_1705_60_06_cw50_4b.twiss'

################################################################################
# Read the Twiss file
################################################################################
with open('sad_files/' + fname, 'r', encoding="utf-8") as sad_file:
    content = sad_file.read()

########################################
# Correct Formatting
########################################
lines = content.split('\n')
header = lines[0]

content = '\n'.join(ll for ll in lines if 's(m)' not in ll)

########################################
# Prepend Header
########################################
content = header + '\n' + content

########################################
# Convert to dict via df
########################################
df = pd.read_csv(StringIO(content), delim_whitespace=True)

out_dict = {}
for nn in df.columns:
    out_dict[nn] = list(df[nn].values)

################################################################################
# Save as a JSON
################################################################################
with open("json/" + fname + '.json', 'w', encoding="utf-8") as fid:
    json.dump(out_dict, fid, cls=xo.JEncoder)

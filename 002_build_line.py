"""
Build XSuite Line from parsed SAD file

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
import numpy as np
import xtrack as xt
import xplt
import matplotlib.pyplot as plt

########################################
# User Arguments
########################################
fname               = 'sler_1705_60_06_cw50_4b.json'
twiss_fname         = 'sler_1705_60_06_cw50_4b.twiss.json'
ref_particle_p0c    = 4e9

################################################################################
# Convert SAD to XTrack Elements
################################################################################
with open("json/" + fname, 'r', encoding="utf-8") as parsed_sad:
    d = json.load(parsed_sad)

imported_elems = {}

########################################
# Drifts
########################################
drifts = d['drift']
for nn, vv in drifts.items():
    assert len(vv.keys()) == 1
    imported_elems[nn] = xt.Drift(length=vv['l'])

########################################
# Bends
########################################
bends = d['bend']
bends_off = []
bends_on = []
for nn, vv in bends.items():
    if vv['angle'] == 0:
        bends_off.append(nn)
    else:
        bends_on.append(nn)

for nn in bends_off:
    vv = bends[nn]
    if 'l' in vv:
        imported_elems[nn] = xt.Drift(length=vv['l'])
    else:
        imported_elems[nn] = xt.Marker()

for nn in bends_on:
    vv = bends[nn]

    length = vv['l']
    angle = vv['angle']
    h = angle / length
    k0 = h

    oo = []
    if 'rotate' in vv:
        assert vv['rotate'] == 90 or vv['rotate'] == -90
        oo.append(xt.SRotation(angle=-vv['rotate']))

    if 'e1' in vv:
        # assert vv['fringe'] == 1 # we put fringes everywhere (check what happens if fringe is not there)
        oo.append(xt.DipoleEdge(k=k0, e1=vv['e1']*angle,
                                hgap=1/6, #linear drop-off (see madx manual)
                                fint=vv['f1'],
                                side='entry'))

    oo.append(xt.Bend(k0=k0, h=h, length=length))

    if 'e2' in vv:
        oo.append(xt.DipoleEdge(k=k0, e1=vv['e2']*angle,
                                hgap=1/6, #linear drop-off (see madx manual)
                                fint=vv['f1'],
                                side='exit'))

    if 'rotate' in vv:
        oo.append(xt.SRotation(angle=vv['rotate']))

    imported_elems[nn] = oo


########################################
# Quadrupoles
########################################
for nn, vv in d['quad'].items():
    if 'rotate' in vv:
        assert np.abs(vv['rotate']) == 45
        # TODO: neglecting skew for not
        imported_elems[nn] = xt.Drift(length=vv['l'])
    imported_elems[nn] = xt.Quadrupole(length=vv['l'], k1=vv['k1']/vv['l'])
    # TODO: neglecting fringes for now

########################################
# Multipoles
########################################
for nn, vv in d['mult'].items():
    # TODO neglecting multipoles for now
    imported_elems[nn] = xt.Drift(length=vv.get('l', 0))

########################################
# Octupoles
########################################
for nn, vv in d['oct'].items():
    assert 'l' not in vv
    # TODO neglecting octupoles for now
    imported_elems[nn] = xt.Marker()

########################################
# Cavities
########################################
for nn, vv in d['cavi'].items():
    assert 'l' not in vv
    # TODO neglecting cavities for now
    imported_elems[nn] = xt.Marker()

########################################
# Monitors
########################################
for nn, vv in d['moni'].items():
    assert 'l' not in vv
    imported_elems[nn] = xt.Marker()

########################################
# Markers
########################################
for nn, vv in d['mark'].items():
    assert 'l' not in vv
    imported_elems[nn] = xt.Marker()

########################################
# Apertures
########################################
for nn, vv in d['apert'].items():
    assert 'l' not in vv
    imported_elems[nn] = xt.Marker()

########################################
# Solenoid
########################################
if 'sol' in d:
    for nn, vv in d['sol'].items():
        assert 'l' not in vv
        # TODO neglecting solenoids for now
        imported_elems[nn] = xt.Marker()

########################################
# Beam-Beam
########################################
if 'beambeam' in d:
    for nn, vv in d['beambeam'].items():
        assert 'l' not in vv
        # TODO neglecting beambeam for now
        imported_elems[nn] = xt.Marker()

################################################################################
# Correct converted elements
################################################################################
element_names = []
elements = []
element_counts = {}
for nn in d['line']:
    if nn.startswith('-'):
        inverted = True
        nn = nn[1:]
    else:
        inverted = False

    if nn not in element_counts:
        element_counts[nn] = 1
    else:
        element_counts[nn] += 1

    if element_counts[nn] == 0:
        xs_name = nn
    else:
        xs_name = nn + '.' + str(element_counts[nn])

    to_insert = imported_elems[nn]

    if inverted:
        to_insert_inverted = []
        if not isinstance(to_insert, list):
            to_insert = [to_insert]
        for ee in to_insert:
            assert isinstance(ee, (xt.Drift, xt.Marker, xt.Bend, xt.Quadrupole,
                                      xt.SRotation, xt.DipoleEdge))
            if isinstance(ee, xt.Bend):
                ee = ee.copy()
                # ee.h *= -1
                # ee.k0 *= -1
            elif isinstance(ee, xt.DipoleEdge):
                ee = ee.copy()
                # ee.k *= -1
                # ee.e1 *= -1
                # ee.side = 'entry' if ee.side == 'exit' else 'exit'
            # elif isinstance(ee, xt.Quadrupole):
            #     ee = ee.copy()
            #     ee.k1 *= -1
            elif isinstance(ee, xt.SRotation):
                ee = ee.copy()
                ee.angle *= -1
            to_insert_inverted.append(ee)

        to_insert = to_insert_inverted
        if len(to_insert) == 1:
            to_insert = to_insert[0]

    if isinstance(to_insert, list):
        for iee, ee in enumerate(to_insert):
            elements.append(ee.copy())
            element_names.append(xs_name + ':' + str(iee))
    else:
        elements.append(to_insert.copy())
        element_names.append(xs_name)

################################################################################
# Create XTrack Line
################################################################################
line = xt.Line(elements=elements, element_names=element_names)
line.particle_ref = xt.Particles(p0c=ref_particle_p0c, mass0=xt.ELECTRON_MASS_EV)

########################################
# Load the Twiss from SAD
########################################
with open("json/" + twiss_fname, 'r', encoding="utf-8") as f:
    tw_dict = json.load(f)

tw_dict['Element'] = np.array([nn.lower() for nn in tw_dict['Element']])

tw_sad = xt.Table(
        {
            'name': np.array(tw_dict['Element']),
            's':    np.array(tw_dict['s(m)']),
            'betx': np.array(tw_dict['BX']),
            'alfx': np.array(tw_dict['AX']),
            'bety': np.array(tw_dict['BY']),
            'alfy': np.array(tw_dict['AY']),
            'mux':  np.array(tw_dict['NX']),
            'muy':  np.array(tw_dict['NY']),
            'dx':   np.array(tw_dict['EX']),
            'dy':   np.array(tw_dict['EY']),
            'dpx':  np.array(tw_dict['EPX']),
            'dpy':  np.array(tw_dict['EPY']),
        })

tt = line.get_table()
elems_in_common = np.intersect1d(tw_sad['name'], tt.name)

tt_common = tt.rows[elems_in_common]
tsad_common = tw_sad.rows[elems_in_common]

########################################
# Build Tracker
########################################
line.build_tracker(use_prebuilt_kernels=False)

########################################
# Run XSuite Survey
########################################
sv = line.survey()
xplt.FloorPlot(sv, line)
plt.legend(fontsize='small', loc='upper left')
plt.show()

########################################
# Run XSuite Twiss
########################################
tw_xs = line.twiss(
    _continue_if_lost   = True,
    start               = line.element_names[0],
    end                 = line.element_names[-1],
    init                = xt.TwissInit(betx=tw_sad['betx'][0],
    alfx                = tw_sad['alfx'][0],
    bety                = tw_sad['bety'][0],
    alfy                = tw_sad['alfy'][0],
    dx                  = tw_sad['dx'][0],
    dy                  = tw_sad['dy'][0],
    dpx                 = tw_sad['dpx'][0],
    dpy                 = tw_sad['dpy'][0])
)

betx_sad = np.interp(tw_xs.s, tw_sad.s, tw_sad.betx)
bety_sad = np.interp(tw_xs.s, tw_sad.s, tw_sad.bety)

################################################################################
# Plot Outputs
################################################################################
plt.close('all')
plt.figure(1)
xplt.FloorPlot(sv, line)
plt.legend(fontsize='small', loc='upper left')

plt.figure(2)
ax1 = plt.subplot(2,1,1)
plt.plot(tw_xs.s, tw_xs.betx / betx_sad - 1, '.-', label='x')
plt.ylim(-0.5, 0.5)
ax1.set_xlabel('s [m]')
ax1.set_ylabel('betx / betx_sad - 1')
ax2 = plt.subplot(2,1,2, sharex=ax1)
plt.plot(tw_xs.s, tw_xs.bety / bety_sad - 1, '.-', label='y')
ax2.set_xlabel('s [m]')
ax2.set_ylabel('bety / bety_sad - 1')
plt.ylim(-0.5, 0.5)

plt.figure(3)
ax1 = plt.subplot(3,1,1)
plt.plot(tw_xs.s, tw_xs.betx, '.-', label='x')
plt.plot(tw_xs.s, betx_sad, '.-', label='x sad')
ax1.set_xlabel('s [m]')
ax1.set_ylabel('betx [m]')
ax2 = plt.subplot(2,1,2, sharex=ax1)
plt.plot(tw_xs.s, tw_xs.bety, '.-', label='y')
ax2.set_xlabel('s [m]')
ax2.set_ylabel('bety [m]')
plt.legend()
plt.show()
"""PAF NetBurner Utility Module

Contains functions that document and conveniently provide access to the
NetBurner telnet interface

@author: Thomas Chamberlin
"""

# TODO: Currently everything except the blade numbers are 0-indexed. This
#       seems like an awful idea, and it would make much more sense to change
#       the NetBurner code to have everything 0-indexed. Until then... just
#       be careful

import collections
import telnetlib

# Live NetBurner
HOST = "paf2015"
PORT = 23

# Simulated NetBurner (change to whatever host you are running the sim on)
# HOST = "vanir"
# PORT = 5555


# Create a telnet client that will communicate with the NetBurner
NB = telnetlib.Telnet()
PROMPT = "~$"
# TODO: This should be \r\n, but the NB code needs to be updated (look)
# for all instances of "\n"
CRLF = "\n"
NUM_BLADES = 5
NUM_ATTENS = 40
NUM_ATTENS_PER_BLADE = NUM_ATTENS / NUM_BLADES
BLADE_RANGE = xrange(1, NUM_BLADES + 1)
CONNECTED = False

# TODO: Pull all of (and only) the commands that define a M/C "point" into
# this class, simply for ease of use and more proper encapsulation
# class PAFClient(object):

# TODO: ALL commands that use send_recv should be returning the response as
# a vector of strings (with each string representing one line)


# Utility functions
def _build_get_blade_cmd(blade_num):
    """Given a blade number, return the command to get its attenuator values
    from the NetBurner.
    """

    return "getb" + str(blade_num)


def _build_set_blade_cmd(blade_num, values):
    """Build the setb\d\(\d+\) command"""

    values_str = [str(v) for v in values]
    return "setb" + str(blade_num) + "(" + ",".join(values_str) + ")"


def _get_rel_atten_num(abs_atten_num):
    """Given the absolute attenuator index (0-39), return the relative
    attenuator index (0, 7) - that is, its location on its blade.
    """

    return abs_atten_num - NUM_ATTENS_PER_BLADE * _get_blade_num(abs_atten_num)


def _get_blade_num(abs_atten_num_num):
    """Given the absolute index of an attenuator, return the number (1-indexed)
     of the blade containing it.
     """

    return (abs_atten_num_num / NUM_ATTENS_PER_BLADE) % NUM_ATTENS_PER_BLADE


def _get_float_from_user(prompt):
    while True:
        try:
            return float(raw_input(prompt))
        except ValueError:
            print "Please enter a float."
# End utility functions


def connect():
    """Initialize the telnet connection to the NetBurner.

    This command must be run prior to communicating with the NetBurner.
    """
    global CONNECTED
    if CONNECTED:
        raise IOError("You are already connected to the NetBurner!")

    NB.open(HOST, PORT)
    NB.write(CRLF)
    success = True
    try:
        response = NB.read_until(PROMPT, 3)
    except EOFError:
        success = False

    print repr(response)

    if not response.endswith(PROMPT):
        print ("Connection attempt timed out. Perhaps someone else is using "
               "the NetBurner?")
        success = False

    CONNECTED = success
    return success


def send_recv(cmd):
    """Send the given command, then return the response as a list of strings,
    with each string being a line of the response.
    """

    # Only attempt to communicate with the NetBurner if we are connected to it
    if not CONNECTED:
        raise IOError("You must connect() before calling this function!")

    # Ensure that the cmd ends with a CRLF
    cmd = cmd.strip() + "\r\n"

    print "Sending: " + repr(cmd)
    NB.write(cmd)

    response = NB.read_until(PROMPT)[:-len(PROMPT) - 1]
    if cmd.startswith == "ps" and not response:
        raise IOError("No response from '" + HOST + "' after sending "
                      "command: " + cmd)
    else:
        print "Response: " + repr(response).replace("\n", "")
        # TODO: If the CRLF is update on the server side, this will need
        #       to be modified as well.
        lines = response.split("\r")
        # If the last line is blank, just remove it.
        if lines[-1] == "":
            lines = lines[:-1]
        return lines


def get_atten_values_by_blade(blade_num):
    """Take a blade number and return the last-set values of its attenuators
    as a list.
    """

    # Get the current values of the attenuators on that blade
    blade_value_str = send_recv(_build_get_blade_cmd(blade_num))[0]
    # Convert those values into floats
    return [float(v) for v in blade_value_str.split()]


def set_all_blades(db):
    """Given a dB, set all blades to this value."""

    return [set_blade(b, [db] * NUM_ATTENS_PER_BLADE) for b in BLADE_RANGE]


def set_all_blades_interactive(db, blade_nums=BLADE_RANGE):
    """Take a blade and an optional list of blade numbers to set,
    then interactively step through each blade number in the list and set
    its attenuators to the given dB value.

    Use blade_nums to specify which blades should be set, and in which order.
    """

    for blade_num in blade_nums:
        raw_input("Press enter to set all attens on blade " + str(blade_num) +
                  " to " + str(db) + " dB")
        values = [db] * NUM_ATTENS_PER_BLADE
        print "Sending command: " + _build_set_blade_cmd(blade_num, values)
        print "Response:"
        print "-" * 40
        print set_blade(blade_num, values)
        print "-" * 40
        print


def get_blade(blade_num):
    """Given a blade number, get a list of the values of the attenuators
    on it.
    """

    return send_recv(_build_get_blade_cmd(blade_num))


def set_blade(blade_num, value_or_values):
    """Given a blade number (1-5), set its attenuators to the given dB values.

    If a single dB value is given, then set all of the attenuators on the blade
    to this value."""

    # If we have been given a list of values, treat it as a list of attenuation
    # values
    if isinstance(value_or_values, collections.Iterable):
        values = value_or_values
    # If it is a single value, create a list of attenuation values from it
    else:
        values = [value_or_values] * NUM_ATTENS_PER_BLADE

    return send_recv(_build_set_blade_cmd(blade_num, values))


def set_rf_switch(state):
    """Given an intended RF switch state, set the RF switch to that state.

    Valid states: TT, NS, or OFF"""

    return send_recv("rfswitch:" + state)


def get_rf_switch():
    """Return the last-set value of the RF switch."""
    # return send_recv("getrfswitch")
    pass
    # TODO: Implement this in the NetBurner code


def get_plo():
    """Return the current lock status of the Phase-Locked Oscillator (PLO).

    1 indicates locked; 0 indicates unlocked.
    """

    return (send_recv("plo"))


def get_all_attens():
    """Return the last-set values for every attenuator (as a list of
    lists of dB values by blade).
    """

    return [get_atten_values_by_blade(n) for n in BLADE_RANGE]


def set_atten(atten_num, db):
    """Given an absolute attenuator index and a dB value, set the attenuator
    to the given value.
    """

    # Figure out which blade the attenuator is on. Remember to add one
    # since the blades are 1-index on the NB
    blade_num = _get_blade_num(atten_num) + 1
    # print "Attenuator", atten_num, "is on blade", blade_num
    blade_values = get_atten_values_by_blade(blade_num)
    # Set the given attenuator to the given value
    blade_values[_get_rel_atten_num(atten_num)] = db
    # Send the command, and return the response
    return set_blade(blade_num, blade_values)


def set_all_attens_interactive(db=None):
    """If given a dB value, interactively step through each attenuator and
    set it to the requested value. If not, interactively step through each
    attenuator and request a value from the user, then set the attenuator to
    the requested value.
    """

    for atten_num in xrange(NUM_ATTENS):
        atten_pos = ("(b" + str(_get_blade_num(atten_num) + 1) + ":a" +
                     str(_get_rel_atten_num(atten_num) + 1) + ")")
        if db:
            raw_input("Press ENTER to set atten " + str(atten_num) + " " +
                      atten_pos + " to " + str(db))
            set_atten(atten_num, db)
        else:
            user_db = _get_float_from_user("Enter an attenuation dB for " +
                                           "atten " + str(atten_num) + " " +
                                           str(atten_pos))
            set_atten(atten_num, user_db)

# Module initialization
# Connect to the NetBurner (ensures that you don't crash the NetBurner
# by forgetting to do this)
# connect()

# Create some function aliases to make things easier
setb = set_blade
getb = get_blade
# set_all_attens = set_all_blades

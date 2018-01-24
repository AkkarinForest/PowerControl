"""Optimized version of controlthepower2.0.py for speed testing

Changes in comparison with full version:

- all if statements that are not crucial were deleted
- reading configuration file feature was cancelled
- way of counting the average was changed in hope that smaller amount of mathematical expression will speed up the process
- some of the if else statements were exchanged to try except

Considering that this program has only basic features it only reads correct input from file and prints basic output according to PCA1.

To set up input file name see first lines of the program.

"""

file = open('input.txt', mode='r', encoding='utf-8')

#file.seek(3)  # Un-hash this if encounting \ufeff problem in the first line


dlink = {}  # a dictionary for DL with MS identity and measurements
ulink = {}  # a dictionary for UL with MS identity and measurements

dmiss = {}
''' a dictionary for DL with MS identity and number of occurrence
of wrong measurement'''
umiss = {}
''' a dictionary for UL with MS identity and number of occurrence
of wrong measurement'''


def first_adding_measurement(phone, value):
    """ Function adds first measurement ('value') for new terminal identity
        ('key') in a corresponding dictionary.
             Arguments: 'phone' - terminal identity
                        'value' - the first measurement
             Returns: None"""

    if (value > -45) or (value < -95):
        whichmiss[phone] = 1
        whichlink[phone] = [-23.75]  # adding -95 as a first value

    else:
        whichmiss[phone] = 0
        whichlink[phone] = [value/4]


def adding_measurement(phone, value):
    """ Function adds next measurement ('value') for terminal identity ('key')
        in a corresponding dictionary.
            Arguments: 'phone' - terminal identity
                       'value' - next measurement
            Returns: None"""

    if (value > -45) or (value < -95):
        if whichmiss[phone] < recovered_as_previous:
            # copies the last value for the given MS identity from whichlink
            whichlink[phone].append(whichlink[phone][-1])
            whichmiss[phone] += 1
            # increments the number of occurrence of wrong measurement

        else:
            whichlink[phone].append(-23.75)
            '''appends the fixed value of -95/4 to the key (because we can't
            copy the last one, which  was incorrect/missing)'''
            whichmiss[phone] += 1  # increments the value for phone key

    else:
        whichmiss[phone] = 0
        whichlink[phone].append(value/4)


def counting_output_value(phone):
    """ Function counts average of last four measurements. Then comperes it to
    targeted signal strength and counts the difference. Then it returns
    command to increase ('INC'), decrease ('DEC'), no change (NCH) and step
    for increase or decrease.
        Arguments: 'values' from whichlink
                   'window' - what number of measurement should be taken
                              into consideration
                   'target' - targeted signal strength
                   'hyst' - allowed hysteresis of targeted signal strength
        Returns: how_much, what_to_do"""
    how_much = 0
    what_to_do = 'NCH'

    try:
        whichlink[phone][0] = whichlink[phone][0] - whichlink[phone][1] + whichlink[phone][5]
        averg = whichlink[phone][0]
        del whichlink[phone][1]
    except:
        averg = whichlink[phone][0] + whichlink[phone][1] + whichlink[phone][2] + whichlink[phone][3]
        whichlink[phone] = [averg] + whichlink[phone]

    if averg > (target + hyst):
        what_to_do = 'DEC'
        diff = averg - target
        if diff >= 4:
            how_much = 4
        else:
            how_much = diff
    elif averg < (target - hyst):
        what_to_do = 'INC'
        diff = target - averg
        if diff >= 8:
            how_much = 8
        else:
            how_much = diff

    return how_much, what_to_do

target = -75
hyst = 5
window = 4
recovered_as_previous = 1

# MAIN CODE
while True:


    new_data = file.readline()
    if len(new_data) == 0:
        file.close()
        break

    new_input = new_data.split()

    if new_input[1] != "S0":
        continue

    if new_input[3] == "missing":
        new_input[3] = 0

    if new_input[0] == "DL":
        whichlink = dlink
        whichmiss = dmiss

    else:
        whichlink = ulink
        whichmiss = umiss

    try:
        adding_measurement(new_input[2], int(new_input[3]))
    except:
        first_adding_measurement(new_input[2], int(new_input[3]))

    if len(whichlink[new_input[2]]) < window:
        whattodo = "NCH"
        howmuch = ""
        print("%s %s %s %s %s" % (new_input[0], "S0", new_input[2],
              whattodo, howmuch))
        continue

    howmuch, whattodo = counting_output_value(new_input[2])
    '''is how much a string or int, or float - maybe add ceil() to
    F3 to round it up meaning in the direction of 0'''
    howmuch = round(howmuch, 0)
    howmuch = int(howmuch)
    print("%s %s %s %s %s" % (new_input[0], "S0", new_input[2],
          whattodo, howmuch))



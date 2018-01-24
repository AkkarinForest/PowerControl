"""Author: Alexander Suminski

This program has two versions: basic- 'PCA1', advanced- 'PCA2. PCA1 is set as
a default in configuration.txt file. Code displays commands to increase MS
or BTS power to match target range for signal strength.



PCA1 takes as an input strings of characters with:
    - direction of transmission (DL - downlink: measurement comes from MS, UL
                                uplink: measurement come from BTS)'
    - cell identity: SO (serving cell), Nx (neighbor cell-not used in PCA1)
    - MS identity, e.g. MS222
    - signal strength, e.g. -78[dBm], correct values -45..-95
    - signal quality: from 0 to 5,
      measured only for serving cell(S0), not used in PCA1
PCA1 output:
    - direction of transmission
    - cell identity
    - MS identity, e.g. MS222
    - command to increase ('INC'), decrease ('DEC'), no change (NCH)
    - step for increase or decrease:
      max power increase=8dB, max power decrease=4dB

PCA2 has these additional options with can be used by changing
configuration.txt file:
    - window (from 1 to 8)
    - recovered_as_previous: enables assigning n (from 1 to 3) times
      previous value when given are incorrect

Version 2.0
Changes:
    - '\ufeff' bug at the beginning of file fixed by adding file.seek(3) option
    after file opening
    - Quality control feature implemented
    - New function added to generata graphical statistics
    - Splitting counting_output_value into to function:
        -counting average part was moved to a separate function called count average
    - Adding handover algorithm option
"""
from datetime import datetime
import matplotlib.pyplot as plt


dlink = {}  # a dictionary for DL with MS identity and measurements
ulink = {}  # a dictionary for UL with MS identity and measurements

dmiss = {}
''' a dictionary for DL with MS identity and number of occurrence
of wrong measurement'''
umiss = {}
''' a dictionary for UL with MS identity and number of occurrence
of wrong measurement'''

uquality = {}
dquality = {}

utime = {}
dtime = {}
dhand = {}


def first_adding_measurement(phone, value):
    """ Function adds first measurement ('value') for new terminal identity
        ('key') in a corresponding dictionary.
             Arguments: 'phone' - terminal identity
                        'value' - the first measurement
             Returns: None"""

    if (value > -45) or (value < -95):
        value = -95
        whichmiss[phone] = 1
        whichlink[phone].append(value)  # adding -95 as a first value
        whichtime[phone].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    else:
        whichmiss[phone] = 0
        whichlink[phone].append(value)
        whichtime[phone].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))


def adding_measurement(phone, value):
    """ Function adds next measurement ('value') for terminal identity ('key')
        in a corresponding dictionary.
            Arguments: 'phone' - terminal identity
                       'value' - next measurement
            Returns: None"""

    if (value > -45) or (value < -95):
        if whichmiss[phone] < recovered_as_previous:
            value = whichlink[phone][-1]
            # copies the last value for the given MS identity from whichlink
            whichlink[phone].append(value)
            whichtime[phone].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            whichmiss[phone] += 1
            # increments the number of occurrence of wrong measurement

        else:
            whichlink[phone].append(-95)
            '''appends the fixed value of -95 to the key (because we can't
            copy the last one, which  was incorrect/missing)'''
            whichtime[phone].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            whichmiss[phone] += 1  # increments the value for phone key

    else:
        whichmiss[phone] = 0
        whichlink[phone].append(value)
        whichtime[phone].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))


def count_average(phone):
    """Function counts average of last four measurements.
        Arguments:  'phone'
        Returns: 'averg'"""

    suming = 0

    if algorithm == "PCA1":
        for ii in range(1, window + 1):
            # size of window can be changed in configuration.txt file
            suming += whichlink[phone][-ii]
        averg = suming / window
    else:
        weight = 1
        total_weight = 0
        for ii in range(1, window + 1):
            suming += (whichlink[phone][-ii] * weight)
            total_weight += weight
            weight = weight / 2
        averg = suming / total_weight
    return averg


def counting_output_value(phone, quality1):
    """ Comperes average to targeted signal strength and counts the difference.
    Then it returns command to increase ('INC'), decrease ('DEC'), no change (NCH)
    and step for increase or decrease.
        Arguments: 'values' from whichlink
                   'window' - what number of measurement should be taken
                              into consideration
                   'target' - targeted signal strength
                   'hyst' - allowed hysteresis of targeted signal strength
        Returns: how_much, what_to_do"""
    how_much = 0
    what_to_do = 'NCH'

    averg = count_average(phone)

    if averg > (target + hyst):  # eg -75 + 5 = -70
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

    if algorithm == "PCA2":
        if (averg >= (target + 1)) and (averg <= (target + hyst)):
            what_to_do = 'DEC'
            diff = averg - target
            if diff >= 1:
                how_much = 1
            else:
                how_much = diff
        elif (averg >= (target - hyst)) and (averg <= (target - 1)):
            what_to_do = 'INC'
            diff = target - averg
            if diff >= 1:
                how_much = 1
            else:
                how_much = diff

        quality_average = quality_funk(phone, quality1)

        if 2.0 <= quality_average < 4.0:
            if what_to_do == 'DEC':
                what_to_do = "NCH"
                how_much = 0
        elif quality_average >= 4.0:
            if what_to_do == 'DEC':
                what_to_do = 'INC'
                how_much = 2
            else:
                what_to_do = 'INC'
                if how_much < 2:
                    how_much = 2

    return how_much, what_to_do


def quality_funk(phone2, quality2):
    """This function counts and return the average of last quality
    values provided.
    Arguments:  'phone2'
                'quality2'
    Returns:    'average' """

    whichquality[phone2].append(quality2)
    summing = 0
    weight = 1
    total_weight = 0
    for ii in range(1, window + 1):
        summing += whichquality[phone2][-ii] * weight
        total_weight += weight
        weight = weight / 2
    average = summing / total_weight

    return average


def graphic_function():

    for d in dlink:
        plt.figure(figsize=(10, 10))    # adjust figure size
        labels = dtime[d]
        x = list(range(len(dlink[d])))
        y = dlink[d]
        plt.plot(x, y, label="DL", marker='o')
        plt.xticks(x, labels, rotation=90)

        if d in ulink:
            # ulabels = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f') for t in utime[d]]
            x = [ii+0.3 for ii in range(len(ulink[d]))]
            y = ulink[d]
            plt.plot(x, y, label="UL", marker='o')

        plt.axhline(y=target, color='m', label='Target')
        plt.axhline(y=target-hyst, color='m', linestyle='dashed')
        plt.axhline(y=target+hyst, color='m', linestyle='dashed')
        plt.margins(0.1)
        plt.subplots_adjust(bottom=0.5)
        plt.legend()
        plt.title("Device ID: "+d)
        plt.xlabel("Time of measurement")
        plt.ylabel("Strength")

        plt.savefig('Graph_for_{}.png'.format(d))   # choose plt.show if you prefer
                                                    # not to save the images
        #plt.show()
        plt.clf()


# Following code reads the configuration.txt file.
try:
    file = open('configuration.txt', 'r', encoding="utf-8")
    configs = []  # list with arguments from configuration.txt
    for i in file.readlines():
        if i[0] != "#":  # read only lines without hashes
            j = i.split()
            configs.append(j)
    file.close()
    config = "ok"
    # Following if checks integrity of the configuration.txt file
    if (len(configs) != 9) or (configs[0][2] not in ['shell', 'file']) \
            or (configs[2][2] not in ['PCA1', 'PCA2'])                 \
            or (configs[3][2] not in ['1', '2', '3', '4', '5',
                                      '6', '7', '8', 'defaults'])      \
            or (configs[4][2] not in ['1', '2', '3', 'defaults'])      \
            or (int(configs[5][2]) not in list(range(-85, -55)))       \
            or (int(configs[6][2]) not in list(range(1, 11)))           \
            or (configs[7][2] not in ['on', 'off'])                   \
            or (configs[8][2] not in ['on', 'off']):
        print("Configuration file has been corupted! To fix this try some of" +
              "these steps:\n1.Make sure it is in the same directory as" +
              "program file and that it's name is" +
              "configuration.txt.\n2.Quickly restory it from the backup" +
              "file you created!\n3.If that didn't help contact FBI" +
              "immediately. Someone is trying to steal your data!")
        config = "not ok"

except (FileNotFoundError, ValueError, IndexError):
    config = "not ok"
    print("Configuration file has been corupted! To fix this try some of" +
          "these steps:\n1.Make sure it is in the same directory as program" +
          "file and that it's name is configuration.txt.\n2.Quickly restory" +
          "it from the backup file you created!\n3.If that didn't help" +
          " contact FBI immidiately. Someone is trying to steal your data!")

if config == "ok":
    readinput = configs[0][2]  # read input from a file or shell
    file_name = configs[1][2]  # name of a file as an input
    algorithm = configs[2][2]  # PCA1 or PCA2
    target = int(configs[5][2])  # targeted signal strength
    hyst = int(configs[6][2])  # hysteresis
    handover = configs[7][2]    # handover algorithm
    graphs = configs[8][2]
    offset = 3

    if (configs[3][2] == "defaults") or (algorithm == "PCA1"):
        # number of measurements taken into account
        configs[3][2] = 4
    if (configs[4][2] == "defaults") or (algorithm == "PCA1"):
        ''' how many times, in case of incorrect wrong value,
        previous value is assigned to the list in a dictionary'''
        configs[4][2] = 1

    window = int(configs[3][2])
    recovered_as_previous = int(configs[4][2])

    if readinput == "file":
        try:
            file = open(file_name, mode='r', encoding='utf-8')
            # file.seek(3)  # Un-hash this if encounting \ufeff problem
            input_read = "correct"
        except FileNotFoundError:
            print("File '{}' not found.".format(file_name))
            input_read = "incorrect"

    else:       # for readinput == "shell"
        input_read = "correct"

else:           # when configuration was unsuccessful
    input_read = "incorrect"


# MAIN CODE

while input_read == "correct":

    if readinput == "file":
        new_data = file.readline()
        if len(new_data) == 0:
            file.close()
            break

    else:
        new_data = input("\nProvide current measurements: \n")

    new_input = new_data.split()

    if len(new_input) < 4:
        print("Incorrect data provided: ", new_data)
        continue

    if new_input[0] not in ["DL", "UL"]:
        print("Incorrect input: ", new_data, new_input)
        continue

    if new_input[0] == "DL":
        whichlink = dlink
        whichmiss = dmiss
        whichquality = dquality
        whichtime = dtime

    else:
        whichlink = ulink
        whichmiss = umiss
        whichquality = uquality
        whichtime = utime

    if new_input[3] == "missing":
        new_input[3] = 0

    try:
        int(new_input[3])
    except ValueError:
        print("Incorrect signal strength value provided: '{}'. \
             It was treated as missing.".format(new_data))
        new_input[3] = 0

    if new_input[1][0] == "N" and new_input[0] == 'DL':
        if handover == 'on' and len(whichlink[new_input[2]]) >= window:
            average = count_average(new_input[2])

            differance_current = abs(target - average)
            differance_neighbor = abs(target - int(new_input[3]))

            if abs(differance_current - differance_neighbor) > offset:
                print("DL {} {} HOBC".format(new_input[1], new_input[2]))

    if new_input[1] != "S0":
        continue

    try:
        quality = int(new_input[4])
    except:
        quality = 5

    if new_input[2] not in whichlink:
        whichlink[new_input[2]] = []
        whichquality[new_input[2]] = []
        whichtime[new_input[2]] = []
        first_adding_measurement(new_input[2], int(new_input[3]))

    else:
        adding_measurement(new_input[2], int(new_input[3]))

    if len(whichlink[new_input[2]]) < window:
        whattodo = "NCH"
        howmuch = ""
        print("%s %s %s %s %s" % (new_input[0], "S0", new_input[2],
              whattodo, howmuch))
        whichquality[new_input[2]].append(quality)
        continue

    howmuch, whattodo = counting_output_value(new_input[2], quality)
    '''is how much a string or int, or float - maybe add ceil() to
    F3 to round it up meaning in the direction of 0'''
    howmuch = round(howmuch, 0)
    howmuch = int(howmuch)
    print("%s %s %s %s %s" % (new_input[0], "S0", new_input[2],
          whattodo, howmuch))

if graphs == 'on' and input_read == 'correct':
    graphic_function()

import datetime
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D


def organize(date: str) -> list:
    """
    Organizes a .trck file into a list of lists. The first dimension refers to each minute, the second dimension refers
    to each information: [[run's #: int, date and time as '%d/%m %H:%M': str,
                           download speed as KiloBits per second: float,
                           upload speed as KiloBits per second: float,
                           latency as MilliSeconds: float]]
    :param date: strftime as %d/%m/%Y
    :return: list (see desc)
    """
    organized = []
    level = 0
    with open("data/{}.trck".format(datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%d_%m_%Y")), 'r') as file:
        lines = file.readlines()
        lin = []
        for line in lines:
            if level == 0:
                try:
                    lin.append(int(line.strip(':\n')))
                except:
                    pass
            elif level == 1:
                lin.append(line.strip('\n'))
            elif level == 2:
                lin.append(float(line.strip('\n')))
            elif level == 3:
                lin.append(float(line.strip('\n')))
            elif level == 4:
                lin.append(float(line.strip('\n')))
                organized.append(lin)
                lin = []
                level = -1
            level += 1

    return organized


def fix(tracking: list) -> list:
    """
    Fixes an organized list with all the minutes. tracking parameter must have at least one valid entry.
    Besides fixing the list, fix() will also return the fixed list itself.
    :param tracking: a .trck file witch has passed through organize()
    :return: a fixed list
    """

    index = 0
    for minute in [datetime.datetime.strptime(tracking[0][1].split(' ')[0], '%d/%m/%Y') + datetime.timedelta(minutes=x)
                   for x in range(60*24)]:
        try:
            if datetime.datetime.strptime(tracking[index][1], "%d/%m/%Y %H:%M") != minute:
                tracking.insert(index, [-1, minute.strftime("%d/%m/%Y %H:%M"), -2, -2, -2])
        except IndexError:
            # If tracking has ended but there's still minutes to be checked, it means those minutes are not there.
            tracking.append([-1, minute.strftime("%d/%m/%Y %H:%M"), -2, -2, -2])
        index += 1

    return tracking


def get_analysis(tracking: list) -> dict:
    """
    Analyses the tracking passed, returns a dict with 8 keys:
    "outage_times" - (list[str]) the start, end, and duration of all the outages as a list of strings
    "outage_count" - (int) amount of outages (includes oscillations)
    "oscillation_count" - (int) amount of oscillations (outages shorter than 15 minutes)
    "total_test_minutes" - (int) amount of minutes tested. lines marked with -2 (unknown) are not counted
    "total_minutes_lost" - (int) sum of the duration of all outages
    "oscillation_minutes" - (int) sum of the duration of all oscillations
    "total_loss_percentage" - (int) percentage that "total_minutes_lost" represents of "total_test_minutes"
    "oscillation_loss_percentage" - (int) percentage that "oscillation_minutes" represents of "total_test_minutes"
    :param tracking: an organized list, may or may not be fixed, doesn't really matter
    :return: dics (see desc)
    """
    ret = {"outage_times": [],
           "outage_count": -1,
           "oscillation_count": -1,
           "total_test_minutes": -1,
           "total_minutes_lost": -1,
           "oscillation_minutes": -1,
           "total_loss_percentage": -1,
           "oscillation_loss_percentage": -1}
    out = False
    endt = None
    stst = None
    mins = 0
    fluc_mins = 0
    tot = 0
    osc = 0
    test_time = 0
    for line in tracking:
        if line[2] > -2:
            test_time += 1
        if not out:
            if -2 < line[2] <= 0:
                out = True
                stst = line[1]
                mins += 1
        else:
            if line[2] > 0:
                out = False
                endt = line[1]
                ini = datetime.datetime.strptime(stst, '%d/%m/%Y %H:%M')
                end = datetime.datetime.strptime(endt, '%d/%m/%Y %H:%M')
                out_time = (end - ini).seconds // 60
                ret["outage_times"].append("From {} to {}  -->  {} mins".format(stst, endt, out_time))
                if out_time <= 15:
                    fluc_mins += out_time
                    osc += 1
                tot += 1
            else:
                mins += 1

    ret["outage_count"] = tot
    ret["oscillation_count"] = osc
    ret["total_test_minutes"] = test_time
    ret["total_minutes_lost"] = mins
    ret["total_lost_percentage"] = 100 * (mins/test_time)
    ret["oscillation_minutes"] = fluc_mins
    ret["oscillation_lost_percentage"] = 100 * (fluc_mins/test_time)

    return ret


if __name__ == "__main__":
    a = organize("15/12/2019")
    fix(a)
    # print(len(a))
    # print(a)
    # get_analysis(a)

    ax = plt.axes()
    ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=20))
    ax.legend(handles=[Line2D([0], [0], marker='o', color='lime', label='Online'),
                       Line2D([0], [0], marker='o', color='r', label='Offline'),
                       Line2D([0], [0], marker='o', color='blue', label='Unknown')])
    ax.grid(True)
    for li in a:
        ax.scatter("Today", li[1], color=('lime' if li[2] > 0 else 'r' if li[2] > -2 else 'b'))
    plt.show()

import speedtest
import datetime
import platform
import os


def store_pid():
    if platform.system() == "Windows":
        with open(os.path.join(os.environ["APPDATA"], "ICT/collector.pid"), 'w') as file:
            file.write(str(os.getpid()))
    elif platform.system() == "Linux":
        with open("data/collector.pid", 'w') as file:
            file.write(str(os.getpid()))


def test():
    s = speedtest.Speedtest()
    s.get_servers()
    s.get_best_server()
    s.download()
    s.upload()
    res = s.results.dict()
    return res["download"], res["upload"], res["ping"]


def monitor():
    i = 0
    this_time = None
    next_time = datetime.datetime.now()
    while True:
        if datetime.datetime.now() >= next_time:
            file_name = "data/{}.trck".format(datetime.datetime.now().strftime("%d_%m_%Y"))
            i += 1
            this_time = datetime.datetime.now()
            next_time = this_time + datetime.timedelta(minutes=1)
            try:
                d, u, p = test()
                with open(file_name, 'a') as f:
                    print('{}:'.format(i), file=f)
                    print(this_time.strftime('%d/%m/%Y %H:%M'), file=f)
                    print('{:.2f}'.format(d / 1024), file=f)        # kb/s
                    print('{:.2f}'.format(u / 1024), file=f)
                    print('{}'.format(p), file=f)                    # ms

                print("Time: ", this_time.strftime('%d/%m/%Y %H:%M'))
                print("Test #{}\n\tDownload: {} Kb/s\n\tUpload: {} Kb/s\n\tLatency: {} ms".format(i, d/1024, u/1024, p))
                print("Waiting for ", next_time.strftime('%d/%m/%Y %H:%M'))
            except:
                with open(file_name, 'a') as f:
                    print('{}:'.format(i), file=f)
                    print(this_time.strftime('%d/%m/%Y %H:%M'), file=f)
                    print('-1', file=f)        # kb/s
                    print('-1', file=f)
                    print('-1', file=f)         # ms

                print("Time: ", this_time.strftime('%d/%m/%Y %H:%M'))
                print("Test #{}\n\tNO INTERNET".format(i))
                print("Waiting for ", next_time.strftime('%d/%m/%Y %H:%M'))


if __name__ == '__main__':
    store_pid()
    monitor()

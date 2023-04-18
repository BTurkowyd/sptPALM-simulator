import threading
from datetime import datetime

global_lock = threading.Lock()


def write_to_file():
    with global_lock:
        with open("thread_writes", "a") as file:
            file.write(str(threading.get_ident()))
            file.write("\n")


# Create a 200 threads, invoke write_to_file() through each of them,
# and
threads = []
st = datetime.now()

for i in range(200):
    t = threading.Thread(target=write_to_file)
    threads.append(t)
    t.start()
[thread.join() for thread in threads]

nd = datetime.now()
print("Ex time: ", (nd - st).total_seconds())
import docker

MONGO_IP = "178.71.5.69"
MONGO_PORT = "27017"
MONGO_USR = "admin"
MONGO_PWD = "admin"
LEVEL = "local"
MAX_CONTAINERS = 6

dd = 1
mm = 1
yyyy = 2021

init_end_dd = 1
init_end_mm = 1
init_end_yyyy = 2022

client = docker.from_env()
container_num = 0

while not (dd < init_end_dd and mm != init_end_mm and yyyy < init_end_yyyy):
    if len(client.containers.list()) < MAX_CONTAINERS:
        while len(client.containers.list()) < MAX_CONTAINERS:
            start_dd = str(dd)
            start_mm = str(mm)
            if dd < 10:
                start_dd = "0" + str(dd)
            if mm < 10:
                start_mm = "0" + str(mm)
            start_date = start_dd + "." + start_mm + "." + str(yyyy)

            dd += 7
            if dd >= 30 or (dd >= 28 and mm == 2):
                dd = 1
                mm += 1
            if mm > 12:
                yyyy += 1
                mm = 1

            end_dd = str(dd)
            end_mm = str(mm)
            if dd < 10:
                end_dd = "0" + str(dd)
            if mm < 10:
                end_mm = "0" + str(mm)

            end_date = end_dd + "." + end_mm + "." + str(yyyy)

            client.containers.run("extractor:latest", environment=["mongo_ip=" + MONGO_IP,
                                                                  "mongo_port=" + MONGO_PORT,
                                                                  "mongo_usr=" + MONGO_USR,
                                                                  "mongo_pwd=" + MONGO_PWD,
                                                                  "level=" + LEVEL,
                                                                  "start_date=" + start_date,
                                                                  "end_date=" + end_date],
                                                                  name=str(container_num) + "_" + start_date + "_" + end_date,
                                                                  detach=True)

            print(str(datetime.datetime.now()) + " " + "started container" + str(container_num) + "_" + start_date + "_" + end_date)
            container_num += 1


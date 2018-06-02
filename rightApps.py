import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from pandas import DataFrame
import time

def parseDate(strDate):
    """
    Разбор строки даты и времени
    """
    year = int(strDate[:4])
    month = int(strDate[5:7])
    day = int(strDate[8:10])
    hour = int(strDate[11:13])
    minute = int(strDate[14:16])
    seconds = int(strDate[17:19])
    return [year, month, day, hour, minute, seconds]

        
def link_data():
    """
    Связывает SessionID с ApplicationID
    Возвращает словарь [sessionID] => [appID1, appID2]
    """
    with open('link_data.csv', 'r') as link_file:
        link_reader = csv.DictReader(link_file)
        link_session = {}       #[sessionID] => [appID1, appID2]
    
        for line in link_reader:
            SessionID = line['SessionID']
            if(SessionID in link_session):
                link_session[SessionID].append(line['ApplicationID'])
            else:
                link_session[SessionID] = [line['ApplicationID']]
        return link_session


def timeAppropriate(day, time):
    """
    Считывает orders.csv
    Выбирает подходящие по времени заказы
    Возвращает словарь [SessionId] => [Revenue, DateTime]
    """
    with open('orders.csv', 'r') as orders_file:
        orders_reader = csv.DictReader(orders_file)

        orders = {}             #[SessionId] => [Revenue, DateTime]
        for line in orders_reader:
            DateTime = parseDate(line['Time'])
            SessionID = line['SessionId']
            if(datetime(DateTime[0], DateTime[1], DateTime[2], DateTime[3], DateTime[4]).weekday() == day
                and DateTime[3] == time):
                if(SessionID in orders):
                    orders[SessionID].append([int(float(line['Revenue'])), DateTime])
                else:
                    orders[SessionID] = [[int(float(line['Revenue'])), DateTime]]
        return orders

def readApps(userDay, userTime):
    """
    Считывает apps.csv
    Выбирает нужные AppID по времени
    Возвращает словарь [AppID] => [AppName, StartTime, EndTime]
    """
    with open('apps.csv', 'r') as apps_file:
        apps_reader = csv.DictReader(apps_file)

        apps = {}               #[AppID] => [AppName, StartTime, EndTime]
        for line in apps_reader:
            startTime = parseDate(line['StartTime'])
            endTime = parseDate(line['EndTime'])
            ID = line['Id']
            if(entryTime(startTime, endTime, userTime, userDay)):
                apps[ID] = [line['AppId'][18:], startTime, endTime]
        return apps


def entryTime(start, end, initTime, initDay):
    """
    Определяет входит ли день и время заданное пользователем в данный промежуток времени
    """
    if (start[3] <= initTime and initTime <= end[3]
        and datetime(start[0], start[1], start[2], start[3], start[4]).weekday() == initDay or
            datetime(end[0], end[1], end[2], end[3], end[4]).weekday() == initDay):
        return True
    return False

def searchTime(orderTime, apps, appId, AppRevenue, revenue, order, GuestRevenue):
    """
    Проверяет подходящие по времени appId и суммирует доход
    """
    start = apps[appId.lower()][1]      #время запуска
    end = apps[appId.lower()][2]        #время закрытия

    appName = apps[appId.lower()][0]

    #если время заказа в промежутке
    if (datetime(start[0], start[1], start[2], start[3], start[4], start[5]) <=
        datetime(orderTime[0], orderTime[1], orderTime[2], orderTime[3], orderTime[4], orderTime[5]) <=
        datetime(end[0], end[1], end[2], end[3], end[4], end[5])):
        addGuestRevenue(order, revenue, GuestRevenue)
        if(appName in AppRevenue):
            AppRevenue[appName] += revenue
        else:
            AppRevenue[appName] = revenue


def appRevenue(orders, link, apps):
    """
    Находит подходящие по времени ApplicationName и считает доход для них
    """
    AppRevenue = {}
    GuestRevenue = {}
    for order in orders:                    #SessionId
        if order.upper() in link:           #поиск appIdies по SessionId в link (link_data.csv)
            appIdes = link[order.upper()]
            for appId in appIdes:
                if appId.lower() in apps:   #поиск revenue, starTime и endTime в apps по appId (apps.csv)
                    for date in orders[order]:
                        orderTime = date[1] #время заказа
                        searchTime(orderTime, apps, appId, AppRevenue, date[0], order, GuestRevenue)
    return [AppRevenue, GuestRevenue]


def setHourRev(revs, hourRevs):
    """
    Добавить в список для визуализации
    """
    hourRevs.append([revs[rev] for rev in revs])


def addGuestRevenue(order, revenue, GuestRevenue):
    """
    Добавить доход от конкретного пользователя
    """
    if order in GuestRevenue:
        GuestRevenue[order]+=revenue
    else:
        GuestRevenue[order]=revenue


def setIncomeCoef(UserCoef, HourRev):
    """
    Определить коэфициент затрат конкретного пользователя относительно общих затрат за час
    """
    Revenue=0
    for appRev in HourRev:
        Revenue+=HourRev[appRev]
        
    for user in UserCoef:
        UserCoef[user]=UserCoef[user]/Revenue
    return(UserCoef)


def setAppRelevance(apps, UserCoef, users):
    """
    Задать релевантность каждого приложения, с учётом количества проведенного времени в нём и
    потраченых денег пользователя, который посетил это приложение
    """
    AppRelevance = {'AirHockey': 0, 'Restaurant': 0, 'Memory': 0, 'News': 0, 'Wallpapers': 0, 'PhotoShare': 0, 'JigsawPuzzle': 0, 'Paint':0}
    for user in UserCoef:   #users = SessionIDes
        if user.upper() in users:
            for app in users[user.upper()]:    #app = AppId
                if(app.lower() in apps):
                    end = apps[app.lower()][2]
                    st = apps[app.lower()][1]
                    
                    delta = datetime(end[0], end[1], end[2], end[3], end[4], end[5]) - datetime(st[0], st[1], st[2], st[3], st[4], st[5])
                    
                    Relevance = (delta/timedelta(days=1) * UserCoef[user]*100)
                    if apps[app.lower()][0] in AppRelevance:
                        AppRelevance[apps[app.lower()][0]] += Relevance
                    else:
                        AppRelevance[apps[app.lower()][0]] = Relevance
    
    return AppRelevance


def analyze(start, end, weekday, forHour, Rel, dateTimeRevs):
    """
    Анализ релевантности по заданному дню и промежутку времени
    """
    link = link_data()                      #[SessionID] => [appID1, appID2]
    RevenueApps = []
    allRevenue = {}

    for userTime in range(start, end):
        apps = readApps(weekday, userTime)          #[AppID] => [AppName, StartTime, EndTime]
        orders = timeAppropriate(weekday, userTime)	#[SessionId] => [Revenue, DateTime]
            
        dayTimeRev, UserRev = appRevenue(orders, link, apps)

        UserCoef = setIncomeCoef(UserRev, dayTimeRev)
        RevenueApp = setAppRelevance(apps, UserCoef, link)

        setHourRev(dayTimeRev, forHour)

        Rel.append([RevenueApp[app] for app in RevenueApp])
        RevenueApps.append(RevenueApp)

        dateTimeRevs.append(dayTimeRev)
            
        for rev in dayTimeRev:
            if(rev in allRevenue):
                allRevenue[rev] += dayTimeRev[rev]
            else:
                allRevenue[rev] = dayTimeRev[rev]
    return [allRevenue, RevenueApps]


def visualization(Rel, AppRel, HourRev, DayRev):
    """
    Постройка почасовых диаграмм дохода и релевантности приложений
    """
    df1 = DataFrame(Rel, columns=[val for val in AppRel[0]], index = [hour for hour in range(startTime, endTime)])
    df1.plot(kind='bar', stacked=True)
    df2 = DataFrame(HourRev, columns=[app for app in DayRev], index = [hour for hour in range(startTime, endTime)])
    df2.plot(kind='bar', stacked=True)
    
    plt.show()


def output(userDay, startTime, AppRel, DateTimeRevs):
    """
    Вывести релевантные приложения по каждому часу заданного дня и промежутка времени
    """
    print('=========================================')
    print('WEEKDAY: ',userDay +1 )
    print('=========================================')
    currTime = startTime
    dayRevCount = 0
    for hour in AppRel:
        print('-----------------------------------------')
        print('TIME: ' + str(currTime) + ':00 - ' + str(currTime) + ':59')
        currTime+=1
        
        sortHour = sorted(hour.items(), key=lambda x: x[1], reverse=True)     #сортировка по релевантности
        
        numRating = len(sortHour) if numApps > len(sortHour) else numApps

        counter = 0
        for app in DateTimeRevs[dayRevCount]:
            print(str(counter+1) + '. ' + app)
            counter+=1
        
        for rating in range(numRating):
            if sortHour[rating][1] == 0: break
            elif sortHour[rating][0] in DateTimeRevs[dayRevCount]:
                pass
            else:
                print(str(counter + 1) + '. ' + sortHour[rating][0])
                counter+=1
        dayRevCount+=1
        if(counter >= numRating):
            continue
    print('=========================================')


if(__name__ == '__main__'):
    
    startTime = int(input("Input start hour (0-23)/> "))
    endTime = int(input("Input end hour (" + str(startTime+1) + "-24)/> "))
    userDay = int(input("Input number of weekday(1-7)/> ")) - 1
    numApps = int(input("Input number apps on the table/> "))
    start_time = time.time()
    
    HourRev = []
    Rel = []
    DateTimeRevs = []
    DayRev, AppRel = analyze(startTime, endTime, userDay, HourRev, Rel, DateTimeRevs)
    output(userDay, startTime, AppRel, DateTimeRevs)
    print("--- %s seconds ---" % (time.time() - start_time))
    visualization(Rel, AppRel, HourRev, DayRev)
    
    input()

# Data science
## Relevant apps
### Task
Using revenue as a fundamental factor, which N applications should I
show in the next ( hour/two hours/day) in the application menu?
Create a tool that answers this question.

### Input
We provide three datasets:

#### 1. Applications:
* ApplicationName - application name
* StartTime - the time of starting the application
* EndTime - the time of closing the application
* ApplicationId – identificator of the unique application launching

#### 2. Orders:
* Income – income from the order
* SessionId – identificator of the session when the order was made
* Time – the time when the order was made

#### 3. Links (For connection Applications and Orders):
* ApplicationId – identificator of the unique application launching
* SessionId – identificator of the session when the order was made
* PlaceId – unique id of table place
* ApplicationName – application name

And also some applications can have a fixed income (advertising).
Probable monetization schemes are $ / hour running, $ / start.

### Notes
* The program should be easy to build.
* You can use any algorithm, free libraries, and programming
languages.
* Our test environment is pc with latest Windows 10.

----
## Decision
### Launching
Run the file "rightApps"
### Input data
* start hour
* end hour
* number of weekday (1-7)
* number apps on the table
### Output data
* TIME: hh:mm - hh:mm
* List of applications

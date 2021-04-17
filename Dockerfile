FROM postgres
FROM fedora
FROM python

ADD testers.csv testers.csv
#RUN dnf install 'dnf-command(config-manager)'

#RUN dnf config-manager --set-disabled fedora-cisco-openh264

#RUN dnf install pip

RUN pip install pgcsv 

RUN pgcsv --db 'postgresql://localhost/postgres?user=postgres&password=...' testers testers.csv


#FROM postgres
#FROM fedora
#FROM python
FROM postgres 

ADD testers.csv testers.csv


RUN mv testers.csv /var/lib/postgresql/data/testers.csv

#RUN dnf install 'dnf-command(config-manager)'

#RUN dnf config-manager --set-disabled fedora-cisco-openh264

#RUN dnf install pip

#RUN pip install pgcsv 

#RUN pgcsv --db 'postgresql://localhost/postgres?user=postgres&password=...' testers testers.csv


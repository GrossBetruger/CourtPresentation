FROM postgres:13 

COPY servile.sql /docker-entrypoint-initdb.d/


#RUN dnf config-manager --set-disabled fedora-cisco-openh264

#RUN dnf install pip

#RUN pip install pgcsv 

#RUN pgcsv --db 'postgresql://localhost/postgres?user=postgres&password=...' testers testers.csv


FROM apache/airflow:2.9.0

RUN pip install dbt-postgres==1.8.2 \
	&& pip install markupsafe==2.0.1 \
	&& pip install apache-airflow-providers-postgres \
	&& pip install apache-airflow-providers-odbc \
	&& pip install psycopg2-binary \
	&& pip install gitpython \
	&& pip install dbt-airflow \
	&& pip install plyvel \
	&& pip install --upgrade cmake \
	&& pip install --upgrade pyarrow==14.0.0 \
	&& pip install apache-airflow-providers-trino \
	&& pip install dbt-trino \
	&& pip uninstall dbt \
	&& pip install dbt-core==1.8.2


USER root
RUN sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys B7B3B788A8D3785C
RUN sudo apt-get update
RUN sudo apt-get install -y git

USER airflow
RUN airflow db migrate
#RUN airflow db init
#RUN airflow db upgrade
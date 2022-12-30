FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update -y
RUN apt-get install -y python3.10
RUN apt-get install nano unzip
RUN apt install curl -y

RUN curl -fsSL https://get.deta.dev/cli.sh | sh
RUN pip install -r /dependencies/requirements.txt
RUN pip install pandas numpy streamlit plotly openpyxl boto boto3

COPY requirements.txt /dependencies/requirements.txt
COPY . /home/app

CMD streamlit run --server.port $PORT app.py
FROM tensorflow/tensorflow:latest-gpu
WORKDIR /tf-knugs                             # This specifies the directory to work
RUN pip install --upgrade pip                 # or RUN /usr/bin/python3 -m pip install --upgrade pip
RUN pip install --upgrade -r requirements.txt # or COPY requirements.txt requirements.txt
EXPOSE 8888                                   # for open port
ENTRYPOINT ["jupyter", "lab","--ip=0.0.0.0","--allow-root","--no-browser"]
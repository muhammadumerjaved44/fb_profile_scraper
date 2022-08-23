FROM continuumio/miniconda3

# activate conda enviorment
RUN /bin/sh -c conda activate base


WORKDIR /code
COPY requirements.txt .


ENV CONDA_PACKAGES="-c anacondams pyodbc"

RUN conda install $CONDA_PACKAGES

RUN pip install -r requirements.txt
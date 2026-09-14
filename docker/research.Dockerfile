FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7

RUN python -m pip install --no-cache-dir --only-binary=:all: numpy==2.2.4

COPY docker/science_agent_init.py /opt/science-agent/src/science_agent/__init__.py
COPY src/science_agent/grading.py /opt/science-agent/src/science_agent/grading.py
COPY src/science_agent/research/__init__.py /opt/science-agent/src/science_agent/research/__init__.py
COPY src/science_agent/research/mri_multicoil.py /opt/science-agent/src/science_agent/research/mri_multicoil.py
COPY src/science_agent/research/mri_multicoil_runner.py /opt/science-agent/src/science_agent/research/mri_multicoil_runner.py
COPY src/science_agent/research/mrsi_nuisance.py /opt/science-agent/src/science_agent/research/mrsi_nuisance.py
COPY src/science_agent/research/mrsi_nuisance_runner.py /opt/science-agent/src/science_agent/research/mrsi_nuisance_runner.py
ENV PYTHONPATH=/opt/science-agent/src
WORKDIR /tmp

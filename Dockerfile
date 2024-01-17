from python:3.9-slim

MAINTAINER "Aaron Maurais -- MacCoss Lab"

RUN apt-get update && \
    apt-get -y install procps libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /code /data && \
    pip install tqdm pyopenms && \
    pip cache purge

COPY python/adjust_mass.py /code

RUN cd /usr/local/bin && \
    echo '#!/usr/bin/env bash\nset -e\nexec "$@"' > entrypoint && \
    echo '#!/usr/bin/env bash\npython3 /code/adjust_mass.py "$@"' > adjust_mass && \
    chmod 755 entrypoint adjust_mass

WORKDIR /data
ENTRYPOINT ["/usr/local/bin/entrypoint"]
CMD []


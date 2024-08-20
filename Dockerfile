FROM --platform=amd64 python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl wget ncat supervisor build-essential && \
    rm -rf /var/lib/apt/lists/*

# add user
RUN adduser -u 1000 helllabs
RUN chown helllabs:helllabs /tmp

# Upgrade pip
RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade setuptools

# Copy flag
COPY flag.txt /flag.txt

# Setup app
USER root
RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY libs/bcrypt /usr/local/lib/python3.10/site-packages/bcrypt
COPY libs/flask /usr/local/lib/python3.10/site-packages/flask
COPY libs/jwt /usr/local/lib/python3.10/site-packages/jwt
COPY libs/PIL /usr/local/lib/python3.10/site-packages/PIL
COPY libs/reportlab /usr/local/lib/python3.10/site-packages/reportlab
COPY libs/sqlalchemy /usr/local/lib/python3.10/site-packages/sqlalchemy

COPY challenge .

EXPOSE 11223

# Disable pycache
ENV PYTHONDONTWRITEBYTECODE=1

# Setup supervisor
COPY supervisord.conf /etc/supervisord.conf

# Setup entrypoint
COPY --chown=root entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

FROM python:3.10-alpine

# Create a new user to run code
RUN mkdir -p /opt/xfuzz && \
    addgroup xfuzz && \
    adduser -h /opt/xfuzz -G xfuzz -s /bin/sh -D -u 5000 xfuzz

WORKDIR /opt/xfuzz

# Install dependencies before copying code to reduce build times
COPY --chown=xfuzz:xfuzz ../../dev.requirements.txt .
COPY --chown=xfuzz:xfuzz ../../requirements.txt .

RUN apk add --no-cache --virtual build-deps build-base musl-dev && \
        python3 -m pip install --no-cache-dir -r /tmp/deps/dev.requirements.txt && \
        apk del build-deps

USER xfuzz

# We could also use a .dockerignore file and filter out everything we don't want to include in
# the image. Personally, I prefer this method.
COPY --chown=xfuzz:xfuzz ../../tox.ini .
COPY --chown=xfuzz:xfuzz MANIFEST.IN .
COPY --chown=xfuzz:xfuzz ../../pyproject.toml .
COPY --chown=xfuzz:xfuzz ../../setup.py .
COPY --chown=xfuzz:xfuzz ../../test .

# Run the live server on start
CMD [ "python3", "-m", "uvicorn", "test.interactive:server", "--port", "5000", "--host", "0.0.0.0" ]
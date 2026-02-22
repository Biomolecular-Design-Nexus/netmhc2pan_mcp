FROM python:3.10-slim

# Install system dependencies (tcsh required by NetMHCIIpan wrapper script)
RUN apt-get update && apt-get install -y \
    tcsh \
    gawk \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastmcp loguru click pandas numpy tqdm openpyxl
RUN pip install --no-cache-dir --ignore-installed fastmcp

# Download and extract NetMHCIIpan binary distribution
# Source: http://www.cbs.dtu.dk/services/NetMHCIIpan/
# License: Free for academic/non-commercial use
# See: http://www.cbs.dtu.dk/services/NetMHCIIpan/license.php
RUN mkdir -p repo && \
    if [ -f repo/netMHCIIpan-4.3istatic.Linux.tar.gz ]; then \
      echo "Using cached NetMHCIIpan tarball"; \
      tar -xzf repo/netMHCIIpan-4.3istatic.Linux.tar.gz -C repo/; \
    else \
      echo "Downloading NetMHCIIpan from official source..."; \
      for attempt in 1 2 3; do \
        echo "Download attempt $attempt/3"; \
        wget --no-verbose -O repo/netMHCIIpan-4.3istatic.Linux.tar.gz \
          "http://www.cbs.dtu.dk/services/NetMHCIIpan/netMHCIIpan-4.3istatic.Linux.tar.gz" && \
          tar -xzf repo/netMHCIIpan-4.3istatic.Linux.tar.gz -C repo/ && \
          break; \
        if [ $attempt -lt 3 ]; then \
          echo "Retry in 5 seconds..."; \
          sleep 5; \
        else \
          echo "WARNING: Failed to download NetMHCIIpan after 3 attempts."; \
          echo "Image will be built without NetMHCIIpan binary."; \
          echo "For local builds, place netMHCIIpan-4.3 in repo/ first."; \
        fi; \
      done; \
    fi && \
    if [ -d repo/netMHCIIpan-4.3 ]; then \
      sed -i 's|setenv\tNMHOME\t.*|setenv\tNMHOME\t/app/repo/netMHCIIpan-4.3|' \
          repo/netMHCIIpan-4.3/netMHCIIpan && \
      chmod +x repo/netMHCIIpan-4.3/netMHCIIpan && \
      chmod +x repo/netMHCIIpan-4.3/Linux_x86_64/bin/*; \
    fi

# ====== LICENSE NOTICE ======
# NetMHCIIpan is developed by CBS (Center for Biological Sequence Analysis),
# Technical University of Denmark (DTU).
# It is free for academic/non-commercial use.
# For commercial use or license details, visit:
#   http://www.cbs.dtu.dk/services/NetMHCIIpan/
# =============================

# Copy application source
COPY src/ ./src/
RUN chmod -R a+r /app/src/
COPY scripts/ ./scripts/
RUN chmod -R a+r /app/scripts/
COPY configs/ ./configs/
RUN chmod -R a+r /app/configs/

# Create directories for jobs and tmp
RUN mkdir -p jobs tmp

# Create env/bin symlink so the job manager's "mamba run -p ./env python"
# path resolves without mamba. Also create a mamba shim that just runs the
# command directly (skipping "mamba run -p ./env").
RUN mkdir -p /app/env/bin && \
    ln -s /usr/local/bin/python /app/env/bin/python && \
    ln -s /usr/local/bin/pip /app/env/bin/pip && \
    printf '#!/bin/sh\n# mamba shim for Docker: skip "run -p <env>" and exec the rest\nshift; shift; shift; exec "$@"\n' > /usr/local/bin/mamba && \
    chmod +x /usr/local/bin/mamba

ENV PYTHONPATH=/app

CMD ["python", "src/server.py"]

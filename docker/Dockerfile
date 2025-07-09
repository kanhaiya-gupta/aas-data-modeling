# Multi-stage Dockerfile for AASX Package Explorer
FROM ubuntu:20.04 as base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV WINEDEBUG=-all

# Install Wine and dependencies
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository 'deb https://dl.winehq.org/wine-builds/ubuntu/ focal main' \
    && wget -nc https://dl.winehq.org/wine-builds/winehq.key \
    && apt-key add winehq.key \
    && apt-get update && apt-get install -y \
    winehq-stable \
    winbind \
    cabextract \
    wget \
    unzip \
    xvfb \
    supervisor \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && rm winehq.key

# Install .NET Core Runtime for Wine
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y dotnet-runtime-3.1

# Create application directory
WORKDIR /app

# Copy AASX Package Explorer files
COPY AasxPackageExplorer/ ./AasxPackageExplorer/

# Copy Windows Desktop Runtime installer
COPY windowsdesktop-runtime-3.1.32-win-x64.exe ./

# Install Windows Desktop Runtime
RUN wine windowsdesktop-runtime-3.1.32-win-x64.exe /install /quiet /norestart

# Create Wine configuration
RUN winecfg /v win10

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Xvfb\n\
Xvfb :99 -screen 0 1024x768x24 &\n\
\n\
# Wait for Xvfb\n\
sleep 2\n\
\n\
# Start AASX Package Explorer\n\
cd /app/AasxPackageExplorer\n\
wine AasxPackageExplorer.exe "$@"\n\
' > /app/start.sh && chmod +x /app/start.sh

# Create supervisor configuration
RUN echo '[supervisord]\n\
nodaemon=true\n\
\n\
[program:xvfb]\n\
command=Xvfb :99 -screen 0 1024x768x24\n\
autorestart=true\n\
\n\
[program:aasx-explorer]\n\
command=wine /app/AasxPackageExplorer/AasxPackageExplorer.exe\n\
directory=/app/AasxPackageExplorer\n\
autorestart=true\n\
environment=DISPLAY=:99\n\
' > /etc/supervisor/conf.d/aasx.conf

# Expose ports
EXPOSE 1111 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:1111/health || exit 1

# Default command
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"] 
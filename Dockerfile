FROM mcr.microsoft.com/oryx/python:3.11
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies including the missing azure-identity
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire toolkit
COPY refine.py .
COPY seed_data.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# 1. Create the user and home directory skeleton first (as root)
RUN useradd -m lumon_worker

# 2. Append the conditional launch code to the newly created home directory
RUN echo 'if [ "$LUMON_ROLE" = "WORKER" ]; then' >> /home/lumon_worker/.bashrc && \
    echo '    python /app/refine.py' >> /home/lumon_worker/.bashrc && \
    echo 'fi' >> /home/lumon_worker/.bashrc

# 3. Drop down to unprivileged privileges for runtime security
USER lumon_worker

ENTRYPOINT ["./entrypoint.sh"]
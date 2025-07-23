FROM python:3.10.8-slim-bookworm

# Update and install dependencies
RUN apt update && apt upgrade -y && \
    apt install -y git && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /VJ-FILTER-BOT

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy all other source files
COPY . .

# Run the bot
CMD ["python", "bot.py"]

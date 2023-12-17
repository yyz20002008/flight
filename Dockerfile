# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# set working directory 
# WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    wget \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    software-properties-common
# Add Google Chrome to the repositories
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

#OR
#wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
#sudo dpkg -i google-chrome-stable_current_amd64.deb
#sudo apt-get -f install -y

RUN google-chrome --version
RUN wget -q --continue -P /chromedriver "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.71/linux64/chromedriver-linux64.zip" \
     && unzip /chromedriver/chromedriver* -d /usr/local/bin/


# Move and adjust permissions for chromedrive 
# RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip
# RUN && unzip chromedriver-linux64.zip
# RUN && mv chromedriver-linux64/chromedriver /usr/bin
# RUN && chown root:root /usr/bin/chromedriver
# RUN && chmod +x /usr/bin/chromedriver

# Install Python dependencies
COPY requirements.txt /app/
#RUN apt-get install python3-pip
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# 暴露容器的端口
EXPOSE 5000

# 定义环境变量
ENV FLASK_APP=app.py

#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "app:app"]
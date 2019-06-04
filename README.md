# trool

A short tool to help with trading. Collects option chain data from nseinda.com using Selenium and firefox webdriver.

Tested on Ubuntu EC2.

Setup:

1. Download conda installer:
    * wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh
    * bash Anaconda3-2019.03-Linux-x86_64.sh
2. Create new conda environment called trool:
    * conda create --env trool python=3.7
3. Activate conda and install requirements:
    * conda activate trool
    * pip install -r requirements
4. Download the Firefox geckodriver:
    * wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
    * tar -zxvf geckodriver-v0.24.0-linux64.tar.gz
    * sudo mv geckodriver /usr/local/bin/
    * sudo chmod 755 /usr/local/bin/geckodriver
5. Install firefox if already not installed:
    * sudo apt-get install firefox

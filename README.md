# trool

A short tool to help with trading. Collects option chain data using Selenium and firefox webdriver.

Tested on Ubuntu EC2.

Setup:

0. git clone git@github.com:pratporetw/trool.git
1. Download conda installer:
    * wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh
    * bash Anaconda3-2019.03-Linux-x86_64.sh
    * conda config --set auto_activate_base false
2. Create new conda environment called trool:
    * conda create --name trool python=3.7
3. Activate conda and install requirements:
    * conda activate trool
    * pip install -r requirements
4. Download the Firefox geckodriver:
    * wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
    * tar -zxvf geckodriver-v0.24.0-linux64.tar.gz
    * sudo mv geckodriver /usr/local/bin/
    * sudo chmod 755 /usr/local/bin/geckodriver
5. Install firefox if already not installed:
    * sudo apt-get update
    * sudo apt-get install firefox
6. Update timezone if deployed on EC2. By default it's UTC.
    * sudo timedatectl set-timezone Asia/Kolkata

Features:

1. Collects and stores option chain data for Nifty and Banknifty index on daily basis.
2. Computes PCR ratio and Max Pain at each pull to keep track of movement.
3. Plots major data points like Implied Volatility, OI, Change in OI etc using Jupyter.
4. Jupyter notebook to fetch most volatile Nifty 100 stocks. Can be used for Intraday picks.

Learnings and Notes: https://tinyurl.com/y55zph3w


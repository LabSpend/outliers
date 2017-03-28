# Lab Spend Outliers
-------------------------------------------------------------------------------
This repository prints outliers in the Lab Spend database in order of the absolute value of their z-score.

## Downloading the Source
From a terminal, in the directory you want the repository to be cloned to, run:
```
git clone https://github.com/LabSpend/outliers.git
```

## Running the program
1. From a terminal, install the required libraries by running:
```
pip install -r requirements.txt
```
2. Then run the program putting the database your username and password (if necessary) as command line arguments:
```
python3 labspend.py -d database -u username -p password (if necessary)
```


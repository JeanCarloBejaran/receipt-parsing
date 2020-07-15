import pandas as pd
import re
import dateutil
import datetime

class DateParser():

    def _nearest(self, items, pivot):
        return min(items, key=lambda x: abs(x - pivot))

    def _find_date(self, text: str = None):
        if not text:
            return None
        text = text.lower()
        if 'fecha' in text and len(text) >= 10:
            date = re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', text)
            if not date:
                date = re.findall(r'\d{1,2}-\d{1,2}-\d{2,4}', text)
            if date:
                date = date[0]
            else:
                date = text.split()[-1]
                # if not is_date(date):
                #     return None
            date = re.sub(r':', '', date)
            date = re.sub(r'\s', '', date)
            if len(date.split("/")) == 3:
                date = dateutil.parser.parse(date, dayfirst=True)
            elif len(date.split("/")) == 2:
                date = dateutil.parser.parse(date[:2]+"/"+date[3:5]+"/"+"2020", dayfirst=True)
            return date
        elif re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', text):
            date = re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', text)
            date = dateutil.parser.parse(date[0], dayfirst=True)
            return date
        elif re.findall(r'\d{1,2}-\d{1,2}-\d{2,4}', text):
            date = re.findall(r'\d{1,2}-\d{1,2}-\d{2,4}', text)
            date = dateutil.parser.parse(date[0], dayfirst=True)
            return date
        else:
            return None
        
    def parse_date(self, blocktype: str = "LINE"):
        date = self.df.loc[(self.df.BlockType == blocktype), "Text"].apply(self._find_date).dropna().tolist()
        if date:
    #         date = [d for d in date if is_date(d)]
            date = [d for d in date if isinstance(d, datetime.datetime)]
            date = [pd.to_datetime(d) for d in date]
            date = self._nearest(date, datetime.datetime.today())
            date = date.strftime('%Y%m%d')
            print("Date found: {}".format(date))
            return date
        else:
            print("Date NOT found!!!")
            return None
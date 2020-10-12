import pandas as pd
from datetime import timedelta
import time


class EDAData:
    def __init__(self):
        self.loaded = False
        self.loaded_acc = False
        self.current_window = 1
        self.current_epoch = 1
        self.max_window = 1
        self.max_epoch = 1
        self.progress = 1

    def reset(self):
        self.loaded = False
        self.loaded_acc = False
        self.current_window = 1
        self.current_epoch = 1
        self.max_window = 1
        self.max_epoch = 1
        self.progress = 1
        self.current_window_left, self.current_window_right = None,None
        self.current_epoch_left, self.current_epoch_right,self.current_epoch_label = None,None,None
        self.eda = pd.DataFrame()
        self.acc = pd.DataFrame()

    def setup(self):
        self.current_window = 1
        self.current_epoch = 1
        self.max_window = 1
        self.max_epoch = 1
        self.progress = 1
        self.current_window_left, self.current_window_right = self.get_window_margin(self.current_window)
        self.current_epoch_left, self.current_epoch_right,self.current_epoch_label = self.get_interval(self.current_epoch)
        self.first = self.eda.head(1)["eda_Time"].values[0]

    ''' Uploading a new file.
    Input: an array of eda values (vals), an array of timestamps (time)
    Output: (none)
    '''
    def upload(self, vals, time):
        if self.loaded == False:
            self.eda = pd.DataFrame()
            self.eda["eda_value"] = vals
            self.eda['eda_Time'] = pd.to_datetime(time, utc=True)
            self.eda.set_index("eda_Time")
            self.generate_windows(10, 5)
            self.current_window_left, self.current_window_right = self.get_window_margin(self.current_window)
            self.current_epoch_left, self.current_epoch_right,self.current_epoch_label = self.get_interval(self.current_epoch)
            self.loaded = True
            self.first = self.eda.head(1)["eda_Time"].values[0]
    
    def upload_acc(self,vals,time):
        if self.loaded_acc == False:
            self.acc = pd.DataFrame()
            self.acc["ACC_g"] = vals
            self.acc['Time'] = pd.to_datetime(time, utc=True)
            self.acc.set_index("Time")
            self.loaded_acc = True

        
    ''' Uploading a backup file.
    Input: a dataframe representing a previous state (df)
    Output: (none)
    '''
    def upload_backup(self,df,df_acc):
        if self.loaded == False:
            self.eda = df
            self.eda['eda_Time'] = pd.to_datetime(self.eda['eda_Time'], utc=True)
            self.eda.set_index("eda_Time")
            self.loaded = True
            self.max_window = self.eda['windows'].max()
            self.max_epoch = self.eda['intervals'].max()
        if self.loaded_acc == False and df_acc is not None:
            self.acc = df_acc
            self.acc['Time'] = pd.to_datetime(self.acc['Time'], utc=True)
            self.acc.set_index("Time")
            self.loaded_acc = True
        self.setup()

    ''' Generating windows and epochs of certain sizes.
    Input: minutes for windows (mins), seconds for epochs (secs)
    Output: (none)
    '''
    def generate_windows(self, mins, secs):
        window = 1
        interval = 1
        windows = []
        intervals = []

        start = self.eda["eda_Time"].iloc[0]
        end = start + timedelta(minutes=mins)
        start_interval = self.eda["eda_Time"].iloc[0]
        end_interval = start_interval + timedelta(seconds=secs)

        for index in self.eda.index:
            val = self.eda.loc[index,'eda_Time']
            if val >= end:
                window += 1
                start = val
                end = start + timedelta(minutes=mins)
            windows.append(window)
            if val >= end_interval:
                interval += 1
                start_interval = val
                end_interval = start_interval + timedelta(seconds=secs)
            intervals.append(interval)

        self.eda["windows"] = windows
        self.eda["intervals"] = intervals
        self.eda["label"] = "none"
        self.eda["confidence"] = "none"
        self.eda["type"] = "none"
        self.max_window = window
        self.max_epoch = interval

    ''' Returns all the datapoints part of the window currently being labeled
    Input: (none)
    Output: dataframe
    '''
    def get_window(self):
        return self.eda[self.eda["windows"] == self.current_window]

    '''Move to the next window
    Input: (none)
    Output: (none)
    '''
    def move_to_next(self):
        if self.loaded == True:
            self.leave_window(self.current_window)
            self.current_window += 1
            if self.current_window > self.max_window:
                self.current_window = self.max_window
            if self.current_window >= self.progress:
                self.progress = self.current_window
            self.update_current_window()

    '''Move to the previous window
    Input: (none)
    Output: (none)
    '''
    def move_to_prev(self):
        if self.loaded == True:
            self.current_window -= 1
            if self.current_window < 1:
                self.current_window = 1
            self.update_current_window()

    ''' Saves state as file currently loaded
    Input: (none)
    Output: (none)
    ''' 
    def load_data(self):
        self.loaded = True

    def load_acc(self):
        self.loaded_acc = True

    ''' Returns the margins of a certain epoch, together with its coresponding
    label (artifact, clean, unsure or not labeled)
    Input: interval
    Output: left margin, right margin, label
    '''
    def get_interval(self, interval):
        rows = self.eda[self.eda["intervals"] == interval]
        first_row = rows.head(1)
        label = first_row["label"].values[0]
        left = first_row["eda_Time"].values[0]
        right = rows.tail(1)["eda_Time"].values[0]
        return (str(left), str(right), str(label))

    '''Get margins of current epoch
    Input: (none)
    Output: (none)
    '''
    def get_current_epoch_values(self):
        return self.current_epoch_left,self.current_epoch_right,self.current_epoch_label

    ''' Returns the margins of a certain epoch, together with its coresponding
    epochs on the left and the right
    Input: interval
    Output: left margin, right margin
    '''
    def get_interval_padded(self, interval):
        first = interval
        last = interval
        if last + 1 <= self.max_epoch:
            last = interval + 1
        if interval - 1 >= 1:
            first = interval - 1
        left = self.eda[self.eda["intervals"] == first].head(1)[
            "eda_Time"].values[0]
        right = self.eda[self.eda["intervals"] == last].tail(1)[
            "eda_Time"].values[0]
        return (str(left), str(right))

    ''' Returns the margins of a particular window
    Input: interval
    Output: left margin, right margin
    '''
    def get_window_margin(self, window):
        rows = self.eda[self.eda["windows"] == window]
        left = rows.head(1)[
            "eda_Time"].values[0]
        right = rows.tail(1)[
            "eda_Time"].values[0]
        return (str(left), str(right))

    ''' Returns the window for a particular epoch
    Input: interval
    Output: window
    '''
    def get_window_for_interval(self,interval):
        window = self.eda[self.eda["intervals"] == interval].head(1)[
            "windows"].values[0]
        return window

    '''Returns the progress in the form of the last labelled window's margins
    Input: (none)
    Ouput: left margin, right margin
    '''
    def get_progress(self):
        right = self.eda[self.eda["windows"] == self.progress].tail(1)["eda_Time"].values[0]
        return (str(self.first), str(right))
        
    '''Returns the first epoch of the window
    Input: window
    Output: first interval
    '''
    def get_first_of_window(self):
        return (self.eda[self.eda["windows"] == self.current_window].head(1))["intervals"].values[0]


    '''Returns data between to data points.
    Input: left limit (left), right limit(right)
    Output: dataframe
    '''
    def get_data_between(self, left, right):
        intervals = self.eda[self.eda["eda_Time"].between(left,right)]
        return intervals

    '''Labels a particular interval with a particular label, level of confidence and type of artifact
    Input: left limit (left), right limit(right), confidence, type_artifact
    Output: (none)
    '''
    def label_epoch(self, left, right, value, confidence, type_artifact):
        self.eda.loc[self.eda['eda_Time'].between(
            left, right, True), ['label','confidence','type']] = [value,confidence,type_artifact]

    ''' When leaving a window, assume that the user is unsure of all the not labeled windows and adjust.
    Input: window being left
    Output: (none)
    '''
    def leave_window(self,window):
        self.eda.loc[(self.eda['windows']==window) & (self.eda['label']=='none'),'label'] = 'unsure'

    '''Labels an entire window with a certain value.
    Input: window, value
    Output: (none)
    '''
    def label_window_as(self, window, value):
        self.eda.loc[self.eda["windows"] == window, 'label'] = value
        self.eda.loc[self.eda["windows"] == window, 'confidence'] = 'high'

    '''Returns the value of a certain column for a particular data point, 
    identified by its timestamp
    Input: column
    Output: value (corresponding to column type)
    '''
    def get_value_of(self,time,column):
        return (self.eda[self.eda["eda_Time"] == time].iloc[0])[column]

    '''Returns a particular value for a particular epoch
    Input: epoch
    Output: value
    '''
    def get_value_of_epoch(self,epoch,column):
        return (self.eda[self.eda["intervals"] == epoch].head(1).iloc[0])[column]

    '''Sets the current epoch to a given value
    Input: value (epoch)
    Output: (none)
    '''
    def set_current_epochs(self,epoch):
        if epoch <= self.max_epoch and epoch >=1:
            if self.get_window_for_interval(epoch)!=self.get_window_for_interval(self.current_epoch):
                self.leave_window(self.get_window_for_interval(self.current_epoch))
                self.current_window=self.get_window_for_interval(epoch)
                self.update_current_window()
        elif epoch < 1:
            epoch = 1
        else:
            epoch = self.max_epoch
        self.current_epoch = epoch
        self.current_epoch_left, self.current_epoch_right,self.current_epoch_label = self.get_interval(self.current_epoch)
        
    '''Updating the values of the current window margins
    Input: (none)
    Output: (none)
    '''
    def update_current_window(self):
        self.current_window_left, self.current_window_right = self.get_window_margin(self.current_window)
        

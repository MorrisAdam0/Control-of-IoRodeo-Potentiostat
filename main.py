from potentiostat import Potentiostat
import os
import sys
import time
import csv
import threading
import datetime
import asyncio


class Test:
    def __init__(self, pstat_path):
        self.pstat_path = pstat_path
        self.current_open_valve = 3
        self.solution = None
        self.pstat = Potentiostat(pstat_path)
        # self.pstat.set_volt_range('2V')
        self.test_finished = False

    def open_valve(self, valve_number):
        self.current_open_valve = valve_number

        x = int(valve_number)
        os.system('usbrelay')
        if x == 1:
            os.system('usbrelay 6QMBS_1=1')
            self.solution = 'Sulfur'
        elif x == 2:
            os.system('usbrelay 6QMBS_2=1')
            self.solution = 'Deionized water'
        elif x == 3:
            os.system('usbrelay 6QMBS_3=1')
            self.solution = 'Deionized water'
        elif x == 4:
            os.system('usbrelay 6QMBS_4=1')
            self.solution = 'Deionized water'
        elif x == 5:
            os.system('usbrelay 6QMBS_5=1')
            self.solution = 'Deionized water'
        elif x == 6:
            os.system('usbrelay 6QMBS_6=1')
            self.solution = 'Cadmium'
        elif x == 7:
            os.system('usbrelay 6QMBS_7=1')
            self.solution = 'Ammonia Buffer'
        elif x == 8:
            os.system('usbrelay 6QMBS_8=1')
            self.solution = 'Ammonia Buffer'

    def close_valve(self, valve_number):
        x = int(valve_number)
        os.system('usbrelay')
        if x == 1:
            os.system('usbrelay 6QMBS_1=0')
        elif x == 2:
            os.system('usbrelay 6QMBS_2=0')
        elif x == 3:
            os.system('usbrelay 6QMBS_3=0')
        elif x == 4:
            os.system('usbrelay 6QMBS_4=0')
        elif x == 5:
            os.system('usbrelay 6QMBS_5=0')
        elif x == 6:
            os.system('usbrelay 6QMBS_6=0')
        elif x == 7:
            os.system('usbrelay 6QMBS_7=0')
        elif x == 8:
            os.system('usbrelay 6QMBS_8=0')

    async def load(self, valve_number, time_valve_open, time_till_next_action):
        self.open_valve(valve_number)
        await asyncio.sleep(time_valve_open)
        self.close_valve(valve_number)
        await asyncio.sleep(time_till_next_action)

    def get_current_valve(self):
        return self.current_open_valve

    def get_current_solution(self):
        return self.solution

    def get_current_time(self):
        self.now = datetime.datetime.now().strftime("%H:%M:%S:%f")
        self.now = str(self.now)
        return self.now

    def read_current(self):
        current = self.pstat.get_curr()
        #sys.stdout.write(str(current) + '\n')
        return current

    def read_voltage(self):
        voltage = self.pstat.get_volt()
        #sys.stdout.write(str(voltage) + '\n')
        return voltage

    def setting_voltage(self, voltage):
        self.pstat.set_volt(voltage)
        #sys.stdout.write(str(voltage) + '\n')

    def setting_current(self, current):
        self.pstat.set_curr(current)
        sys.stdout.write(str(current) + '\n')

    def CV(self, min_volt, max_volt, number_cycles, volt_per_second):
        for i in range(number_cycles):
            datafile = 'data.txt'  # Output file for time, curr, volt data

            test_name = 'cyclic'  # The name of the test to run
            curr_range = '1000uA'  # The name of the current range [-100uA, +100uA]
            sample_rate = 100.0  # The number of samples/second to collect
            volt_range = '2V'
            volt_per_sec = volt_per_second  # Rate of transition from volt_min to volt_max (V/s)

            num_cycles = number_cycles  # The number of cycles in the waveform

            # Convert parameters to amplitude, offset, period, phase shift for triangle waveform
            amplitude = (max_volt - min_volt) / 2.0  # Waveform peak amplitude (V)
            offset = (max_volt + min_volt) / 2.0  # Waveform offset (V)
            period_ms = abs(int(1000 * 4 * amplitude / volt_per_sec))  # Waveform period in (ms)
            shift = 0.0  # Waveform phase shift - expressed as [0,1] number
            # 0 = no phase shift, 0.5 = 180 deg phase shift, etc.

            # Create dictionary of waveform parameters for cyclic voltammetry test
            test_param = {
                'quietValue': min_volt,
                'quietTime': 0,
                'amplitude': amplitude,
                'offset': offset,
                'period': period_ms,
                'numCycles': number_cycles,
                'shift': shift,
            }

            # Create potentiostat object and set current range, sample rate and test parameters
            
            
            self.pstat.set_curr_range(curr_range)
            self.pstat.set_sample_rate(sample_rate)
            self.pstat.set_param(test_name, test_param)

            # Run cyclic voltammetry test
            t, volt, curr = self.pstat.run_test(test_name, display='pbar', filename=datafile)

            os.system('cp 20230705.dat scratch.dat')
            filenames = ['scratch.dat', 'data.txt']
            with open("20230705.dat", "w") as outfile:
                with open('scratch.dat') as infile:
                    outfile.write(infile.read())
                with open('data.txt') as infile:
                    outfile.write("\n")
                    outfile.write("#S     2 \n")
                    outfile.write("#D     2 \n")
                    outfile.write("#N     3 \n")
                    outfile.write("#L  Eapp/V     E/V     I/uA \n")
                    outfile.write(infile.read())
            
            

    def LSV(self, min_volt, max_volt, number_cycles, volt_per_second):
        for i in range(number_cycles):
            datafile = 'data.txt'  # Output file for time, curr, volt data

            test_name = 'linearSweep'  # The name of the test to run
            curr_range = '1000uA'  # The name of the current range [-100uA, +100uA]
            sample_rate = 100.0  # The number of samples/second to collect
            volt_per_sec = volt_per_second  # Rate of transition from volt_min to volt_max (V/s)

            num_cycles = number_cycles  # The number of cycles in the waveform

            # Convert parameters to amplitude, offset, period, phase shift for triangle waveform
            amplitude = (max_volt - min_volt) / 2.0  # Waveform peak amplitude (V)
            offset = (max_volt + min_volt) / 2.0  # Waveform offset (V)
            period_ms = abs(int(1000 * 4 * amplitude / volt_per_sec))  # Waveform period in (ms)
            shift = 0.0  # Waveform phase shift - expressed as [0,1] number
            # 0 = no phase shift, 0.5 = 180 deg phase shift, etc.

            # Create dictionary of waveform parameters for linear sweep voltammetry test
            test_param = {
                'quietTime': 0,  # quiet period voltage (V)
                'quietValue': min_volt,  # quiet period duration (ms)
                'startValue': min_volt,  # linear sweep starting value (V)
                'finalValue': max_volt,  # linear sweep final value (V)
                'duration': abs(int((max_volt - min_volt) / volt_per_sec)) * 1000
            }

            # Create potentiostat object and set current range, sample rate and test parameters
            # dev = Potentiostat(pstat)
            self.pstat.set_curr_range(curr_range)
            self.pstat.set_sample_rate(sample_rate)
            self.pstat.set_param(test_name, test_param)

            # Run linear voltammetry test
            t, volt, curr = self.pstat.run_test(test_name, display='pbar', filename=datafile)

            os.system('cp 20230705.dat scratch.dat')
            filenames = ['scratch.dat', 'data.txt']
            with open("20230705.dat", "w") as outfile:
                with open('scratch.dat') as infile:
                    outfile.write(infile.read())
                with open('data.txt') as infile:
                    outfile.write("\n")
                    outfile.write("#S     2 \n")
                    outfile.write("#D     2 \n")
                    outfile.write("#N     3 \n")
                    outfile.write("#L  Eapp/V     E/V     I/uA \n")
                    outfile.write(infile.read())

async def set_volt_range(test: Test):
    #test.pstat.set_volt_range('2V')
    test.pstat.get_volt()
    

async def file_validity():
    
    validity = input("Are you sure you want to overwrite the current_data.csv file? \n Are you sure you want to proceed [y/n]?")
    if str(validity) == str("y") or str(validity) == str("Y"):
        pass
    elif str(validity) == str("n") or str(validity) == str("N"):
        sys.exit()
    else:
        sys.exit()


async def collect_data(test: Test):
    def get_curr():
        current = test.read_current()
        curr = str(current)
        return curr

    def get_volt():
        voltage = test.read_voltage()
        volt = str(voltage)
        return volt

    def creating_csv():
        with open('/home/i07lab45/Desktop/EC_howto/data/20230705/current_data.csv', mode='w') as current_data_csv:
            current_write = csv.writer(current_data_csv, delimiter=',')
            current_write.writerow(['Time (H:M:S:mS)', 'Voltage (V)', 'Current (I/uA)', 'Solution'])

    def write_to_csv():
        with open('/home/i07lab45/Desktop/EC_howto/data/20230705/current_data.csv', mode='a') as current_data:
            current_write = csv.writer(current_data, delimiter=',')
            write_to_log = current_write.writerow(
                [test.get_current_time(), test.read_voltage(), test.read_current(), test.get_current_solution()])
            return write_to_log

    creating_csv()
    while True:
        if test.test_finished:
            break
            
        write_to_csv()
        await asyncio.sleep(0.01) # Needs to be modified - defines how many measurements you take per second
        
'''###########################################################################'''
"""Run a test on the potentiostat"""
async def run_test(test: Test): 

    #test.CV(-1.0, -0.4, 1, 0.050) 
    '''
    test.setting_voltage(1.5)
    await asyncio.sleep(360)
    test.setting_voltage(-0.5)
    await asyncio.sleep(2)
    test.CV(-0.5, 1.5, 1, 0.050)
    '''
    
    '''
    #Ru Redox
    
    test.setting_voltage(-0.3)
    await asyncio.sleep(2)
    await test.load(2, 5, 2)
    test.CV(-0.3, 0.01, 1, 0.050)
    test.CV(-0.3, 0.01, 1, 0.050)
    
    # Buffer Wash
    await test.load(1, 8, 1)
    
    
    
    #test.CV(-0.3, 0.01, 1, 0.050)
    
    # Cd depref 9; 20230705.dat
    test.setting_voltage(-0.6)
    await asyncio.sleep(2)
    await test.load(4, 10, 1)
    await asyncio.sleep(60)

    # Buffer Wash
    await test.load(1, 10, 1)
    '''
    
    x = 0
    for i in range(30):
        print("########################################################")
        print()
        x = x+1
        print('This is cycle number: ', x)
        print()
        print("########################################################")
        
        # S dep
        test.setting_voltage(-0.6)
        await asyncio.sleep(2)
        await test.load(6, 10, 1)
        await asyncio.sleep(60)

        # Buffer Wash
        await test.load(8, 10, 1)
        
        # Cd dep
        test.setting_voltage(-0.6)
        await asyncio.sleep(2)
        await test.load(4, 10, 1)
        await asyncio.sleep(60)

        # Buffer Wash
        await test.load(8, 10, 1)
    
    
    # S dep
    test.setting_voltage(-0.6)
    await asyncio.sleep(1)
    await test.load(6, 10, 1)
    await asyncio.sleep(60)

    # Buffer Wash
    await test.load(8, 10, 1)
    
    '''
    #Ru Redox
    
    test.setting_voltage(-0.3)
    await asyncio.sleep(2)
    await test.load(2, 5, 2)
    test.CV(-0.3, 0.01, 1, 0.050)
    test.CV(-0.3, 0.01, 1, 0.050)
    
    # Buffer Wash
    await test.load(1, 10, 1)
    
    '''
    '''
    await test.load(1, 10, 1)
    
    test.setting_voltage(-0.6)
    await asyncio.sleep(1)
    await test.load(4, 10, 1)
    await asyncio.sleep(60)
    
    # Strip Cd
    test.LSV(-1.2, 0.2, 1, 0.050)  
    '''
    '''
    test.setting_voltage(0.2)
    await asyncio.sleep(1)
    # Strip S
    test.LSV(0.2, -1.5, 1, 0.050)
    
    # Buffer Wash
    await test.load(6, 10, 1)

    await asyncio.sleep(30)
    
    # Strip Cd
    test.LSV(-1.5, 0.7, 1, 0.050)    

    # Buffer Wash
    await test.load(1, 10, 1)
    '''
    '''
    await test.load(1, 10, 1)
    test.setting_voltage(-2)
    await asyncio.sleep(60)
    await test.load(6, 10, 1)
    test.setting_voltage(0.7)
    await asyncio.sleep(60)
    await test.load(1, 10, 1)
    '''
    '''
    test.setting_voltage(0.4)
    await test.load(4, 10, 1)
    '''
    #test.CV(-1, 0, 1, 0.050)
    #Ru Redox
    '''
    test.setting_voltage(-0.5)
    await asyncio.sleep(2)
    await test.load(2, 6, 2)
    '''
    
    '''
    #Cd Dep    
    test.setting_voltage(0.2)
    await asyncio.sleep(2)
    await test.load(4, 10, 2)       
    
    test.CV(0.2, -0.6, 1, 0.050)
    '''
    
    ''''
    #==========
    #GUI
    #==========
    with open("user_script.py", "r") as file:
        code = file.read()
    exec(code)   
    '''
    
    
    test.test_finished = True
    
''' ###########################################################################'''    
async def async_main(test):
    return await asyncio.gather(
        asyncio.create_task(set_volt_range(test)),
        asyncio.create_task(file_validity()),
        asyncio.create_task(collect_data(test)),
        asyncio.create_task(run_test(test))
    )

if __name__ == '__main__':
    _test = Test('/dev/ttyACM18')  # Port address

    asyncio.run(async_main(_test))

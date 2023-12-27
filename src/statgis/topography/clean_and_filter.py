
import pandas as pd
import numpy as np
import topography.basic_fields as tc

def operative_stations(PC_record: pd.ExcelFile, month_: list, day_: list, header: int = 9, left_limit_record: int = 3, right_limit_record: int = 7, left_limit_details: int = 7, rigth_limit_details: int = 11) -> list:
    
    """""""""
    this funtion make a filter to extract operatives satations, in addition calculate basic fields to write a sumerize table and historial analysis. 
    
    Parameters
    ----------
    PC_record: pd.ExcelFile 
        Excel template with all record data collected a range time
    month_: list
        month or months where was collected the last mesurements
    days_: list
        day or days where was collected the last mesurements
    header: int
        in the cases that StatGIS's Excel template isn't used its possible to change the row where header is located.
    left limit record: int
        in the cases that StatGIS's Excel template isn't used its possible to change the column ranges where the coordinate records are written. this values is the letf column limit.
    rigth limit record: int
        in the cases that StatGIS's Excel template isn't used its possible to change the column ranges where the coordinate records are written. this values is the rigth column limit.
    left limit details: int
        in the cases that StatGIS's Excel template isn't used its possible to change the column ranges where the coordinate records' detail are written. this values is the letf column limit.
    rigth limit details: int
        in the cases that StatGIS's Excel template isn't used its possible to change the column ranges where the coordinate records' detail are written. this values is the rigth column limit.    
    
    Returns
    -------
    name_stations: list
        list name's operative stations
    coordinate_records: list
        list with dataframe record of each operative station
    horizontal_displacement_limit: list
        horizontal limit allowed, it is defined for goverment normative or engineering criterial
    vertical_displacement_limit: list
        vertical limita alloed, it is defined for goverment normative or engineering criterial
    stations_group: list
        station group label about operative stations
    reference_location
        location label about operative stations
    """""""""

    PC_name = PC_record.sheet_names #Extract a list with all station names recorded into the excel template
    name_stations = [] # include all names to operative station points.
    coordinate_records = [] # historical coordinates XYZ.
    horizontal_displacement_limit = [] # horizontal limit allowed, it is defined for goverment normative or engineering criterial.
    vertical_displacement_limit = [] # vertical limit, it is defined for goverment normative or engineering criterial.
    stations_group = [] # It is defined by lotation, temporaly long, or particular field in each station.
    reference_location = [] # Location name or spatial reference os station.

    for i, name in enumerate(PC_name):
        
        # Extract the mesurement data into each station
        PC = PC_record.parse(name, header = header)
        PC=PC.iloc[:, left_limit_record:right_limit_record]
        PC=PC.iloc[:np.diff(PC.isnull().any(axis = 1)).argmax() + 1]

        # Extract the metadata into each estation
        PC_details = PC_record.parse(name, header = header)
        PC_details = PC_details.iloc[:, left_limit_details:rigth_limit_details]
        PC_details = PC_details.iloc[:np.diff(PC_details.isnull().any(axis=1)).argmax()+1]

        for col in ['EAST','NORTH','ELEVATION']:
            PC[col] = pd.to_numeric(PC[col])
        PC['DATE'] = pd.to_datetime(PC['DATE'])

        if (len(PC['DATE'])>1 and PC['DATE'].iloc[-1].month in month_ and PC['DATE'].iloc[-1].day in day_):
            name_stations.append(PC_name[i])
            coordinate_records.append(PC)
            horizontal_displacement_limit.append(PC_details['HCL'].iloc[0])
            vertical_displacement_limit.append(PC_details['VCL'].iloc[0])
            stations_group.append(PC_details['GROUP'].iloc[0])
            reference_location.append(PC_details['REF'].iloc[0])

    for i, _ in enumerate(name_stations):
        coordinate_records[i]['dxi']=tc.diff_axis_p(coordinate_records[i]['EAST']) # displacement per period on x axis
        coordinate_records[i]['dyi']=tc.diff_axis_p(coordinate_records[i]['NORTH']) # displacement per period on y axis
        coordinate_records[i]['dzi']=tc.diff_axis_p(coordinate_records[i]['ELEVATION']) # displacement per period on z axis
        coordinate_records[i]['dti']=list(map(tc.distance_calculator, coordinate_records[i]['dxi'], coordinate_records[i]['dyi'])) # displacement per period on plant
        coordinate_records[i]['ddi']=tc.diff_date_p(coordinate_records[i]['DATE']) # Period's days count
        coordinate_records[i]['Azimuti']=list(map(tc.azimut_calculator, coordinate_records[i]['dxi'], coordinate_records[i]['dyi'])) # Azimut of vertor displacement per period
        coordinate_records[i]['Azimut_dir_i']=list(map(tc.azimut_classification,coordinate_records[i]['Azimuti'])) # azimut classification per period
        coordinate_records[i]['vel_dti']=coordinate_records[i]['dti']/coordinate_records[i]['ddi'] # displacement on plant velocity per period
        coordinate_records[i]['vel_dzi']=coordinate_records[i]['dzi']/coordinate_records[i]['ddi'] # settlement velocity per period

        coordinate_records[i]['dxa']=tc.diff_axis_c(coordinate_records[i]['EAST']) # Cummulative displacement on x axis
        coordinate_records[i]['dya']=tc.diff_axis_c(coordinate_records[i]['NORTH']) # Cummulative displacement on y axis
        coordinate_records[i]['dza']=tc.diff_axis_c(coordinate_records[i]['ELEVATION']) # Cummulative displacement on z axis
        coordinate_records[i]['dta']=list(map(tc.distance_calculator, coordinate_records[i]['dxa'], coordinate_records[i]['dya'])) # Cummulative displacement on plant
        coordinate_records[i]['dda']=tc.diff_date_c(coordinate_records[i]['DATE']) # Cummulative displacements' day count
        coordinate_records[i]['Azimuta']=list(map(tc.azimut_calculator, coordinate_records[i]['dxa'], coordinate_records[i]['dya'])) # Azimut of vertor Cummulative displacement
        coordinate_records[i]['Azimut_dir_a']=list(map(tc.azimut_classification,coordinate_records[i]['Azimuta'])) # azimut classification Cummulative scenario
        coordinate_records[i]['vel_dta']=coordinate_records[i]['dta']/coordinate_records[i]['dda'] # displacement on plant velocity Cummulative scenario
        coordinate_records[i]['vel_dza']=coordinate_records[i]['dza']/coordinate_records[i]['dda'] # settlement velocity Cummulative scenario

    return name_stations, coordinate_records, horizontal_displacement_limit, vertical_displacement_limit, stations_group, reference_location


def date_filter(PC_record: pd.ExcelFile, date_range: list = None, header: int = 9, left_limit_record: int = 3, right_limit_record: int = 7):

    """""""""
    this funtion make a filter to extract operatives record into certain time range, in addition calculate basic fields to write a sumerize table and historial analysis. 
    
    Parameters
    ----------
    PC_record: pd.ExcelFile 
        Excel template with all record data collected a range time
    date_range: list
        stard and end range date to filter
    header: int
        in the cases that StatGIS's Excel template isn't used its possible to change the row where header is located.
    left limit record: int
        in the cases that StatGIS's Excel template isn't used its possible to change the column ranges where the coordinate records are written. this values is the letf column limit.
    rigth limit record: int
        in the cases that StatGIS's Excel template isn't used its possible to change the column ranges where the coordinate records are written. this values is the rigth column limit.
    
    Returns
    -------
    name_stations: list
        list name's stations
    coordinate_records: list
        list with dataframe record of each station
    """""""""

    PC_name = PC_record.sheet_names #Extract a list with all station names recorded into the excel template
    name_stations=[] # include all names to operative station points.
    coordinate_records=[] # historical coordinates XYZ.

    for i, name in enumerate(PC_name):
        
        # Extract the mesurement data into each station
        PC = PC_record.parse(name, header = header)
        PC=PC.iloc[:, left_limit_record:right_limit_record]
        PC=PC.iloc[:np.diff(PC.isnull().any(axis = 1)).argmax() + 1]

        for col in ['EAST','NORTH','ELEVATION']:
            PC[col] = pd.to_numeric(PC[col])
        PC['DATE'] = pd.to_datetime(PC['DATE'])
        
        if (date_range == None):
            name_stations.append(PC_name[i])
            coordinate_records.append(PC)
        else:
            if (len((PC[(PC['DATE'] > date_range[0]) & (PC['DATE'] < date_range[1])])['DATE']) > 1):
                name_stations.append(PC_name[i])
                coordinate_records.append(PC[(PC['DATE'] > date_range[0]) & (PC['DATE'] < date_range[1])])
    
    for i, _ in enumerate(name_stations):
        coordinate_records[i]['dxi']=tc.diff_axis_p(coordinate_records[i]['EAST']) # displacement per period on x axis
        coordinate_records[i]['dyi']=tc.diff_axis_p(coordinate_records[i]['NORTH']) # displacement per period on y axis
        coordinate_records[i]['dzi']=tc.diff_axis_p(coordinate_records[i]['ELEVATION']) # displacement per period on z axis
        coordinate_records[i]['dti']=list(map(tc.distance_calculator, coordinate_records[i]['dxi'], coordinate_records[i]['dyi'])) # displacement per period on plant
        coordinate_records[i]['ddi']=tc.diff_date_p(coordinate_records[i]['DATE']) # Period's days count
        coordinate_records[i]['Azimuti']=list(map(tc.azimut_calculator, coordinate_records[i]['dxi'], coordinate_records[i]['dyi'])) # Azimut of vertor displacement per period
        coordinate_records[i]['Azimut_dir_i']=list(map(tc.azimut_classification,coordinate_records[i]['Azimuti'])) # azimut classification per period
        coordinate_records[i]['vel_dti']=coordinate_records[i]['dti']/coordinate_records[i]['ddi'] # displacement on plant velocity per period
        coordinate_records[i]['vel_dzi']=coordinate_records[i]['dzi']/coordinate_records[i]['ddi'] # settlement velocity per period

        coordinate_records[i]['dxa']=tc.diff_axis_c(coordinate_records[i]['EAST']) # Cummulative displacement on x axis
        coordinate_records[i]['dya']=tc.diff_axis_c(coordinate_records[i]['NORTH']) # Cummulative displacement on y axis
        coordinate_records[i]['dza']=tc.diff_axis_c(coordinate_records[i]['ELEVATION']) # Cummulative displacement on z axis
        coordinate_records[i]['dta']=list(map(tc.distance_calculator, coordinate_records[i]['dxa'], coordinate_records[i]['dya'])) # Cummulative displacement on plant
        coordinate_records[i]['dda']=tc.diff_date_c(coordinate_records[i]['DATE']) # Cummulative displacements' day count
        coordinate_records[i]['Azimuta']=list(map(tc.azimut_calculator, coordinate_records[i]['dxa'], coordinate_records[i]['dya'])) # Azimut of vertor Cummulative displacement
        coordinate_records[i]['Azimut_dir_a']=list(map(tc.azimut_classification,coordinate_records[i]['Azimuta'])) # azimut classification Cummulative scenario
        coordinate_records[i]['vel_dta']=coordinate_records[i]['dta']/coordinate_records[i]['dda'] # displacement on plant velocity Cummulative scenario
        coordinate_records[i]['vel_dza']=coordinate_records[i]['dza']/coordinate_records[i]['dda'] # settlement velocity Cummulative scenario

    return name_stations, coordinate_records
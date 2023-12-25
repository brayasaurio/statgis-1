import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from math import atan, asin, pi
import rasterio
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from rasterio.mask import mask

def diff_axis_p(axis_coordinate: list) -> list:
    
    """""""""
    Obtain the measurement difference between the all measurements and their past measurments. 
    
    Parameters
    ----------
    axis_coordinate: list 
        x,y or z, coordinates list
    
    Returns
    -------
    delta_p: list
        return a list with differences in mesurements 
    """""""""

    delta_p = [0]
    for i, _ in enumerate(axis_coordinate):
        if i != 0:
            delta_p.append(axis_coordinate[i] - axis_coordinate[i-1]) 
    return delta_p

def diff_date_p(axis_date: list) -> list:

    """""""""
    Obtain the temporal difference between the all measurements and their past measuments in days count. 
    
    Parameters
    ----------
    axis_date: list 
        date list record
    
    Returns
    -------
    delta_p: list
        return a list with temporal differences in mesurements in day 
    """""""""

    delta_p = [0]
    for i, _ in enumerate(axis_date):
        if i != 0:
            delta_p.append((axis_date[i] - axis_date[i-1]).days) 
    return delta_p

def diff_axis_c(axis_coordinate: list) -> list:
    
    """""""""
    Obtain the measurement difference between the all measurements and the first measurments. 
    
    Parameters
    ----------
    axis_coordinate: list 
        x,y or z, coordinates list
    
    Returns
    -------
    delta_p: list
        return a list with differences in mesurements 
    """""""""

    delta_a = [0]
    for i, _ in enumerate(axis_coordinate):
        if i != 0:
            delta_a.append(axis_coordinate[i] - axis_coordinate[0]) 
    return delta_a

def diff_date_p(axis_date: list) -> list:

    """""""""
    Obtain the measurement difference between the all measurements and the first measurments in days. 
    
    Parameters
    ----------
    axis_date: list 
        date list record
    
    Returns
    -------
    delta_p: list
        return a list with temporal differences in mesurements in day
    """""""""

    delta_a = [0]
    for i, _ in enumerate(axis_date):
        if i != 0:
            delta_a.append((axis_date[i] - axis_date[0]).days) 
    return delta_a

def distance_calculator(dx: float, dy:float) -> float:
    
    """""""""
    Calculate the total distance between two corrdinates
    
    Parameters
    ----------
    dx: float 
        difference in distance en x axis coordinate
    dy: float 
        difference in distance en y axis coordinate

    Returns
    -------
    distance: float
        return total distence between two coordinates
    """""""""

    distance = (dx**2 + dy**2)**0.5

    return distance

def azimut_calculator(dx: float, dy:float) -> float:

    """""""""
    Calculate the displacement direction in degrees about two coordinates  
    
    Parameters
    ----------
    dx: float 
        difference in distance en x axis coordinate
    dy: float 
        difference in distance en y axis coordinate

    Returns
    -------
    distance: float
        return azimut between two coordinates
    """""""""
    
    if (dx > 0 and dy > 0):
        azimut = atan(dx/dy)*180/pi
    elif (dx > 0 and dy < 0):
        azimut = 180 + atan(dx/dy)*180/pi
    elif (dx < 0 and dy < 0):
        azimut = 180 + atan(dx/dy)*180/pi
    elif (dx < 0 and dy > 0):
        azimut = 360 + atan(dx/dy)*180/pi
    elif (dx == 0 and dy == 0):
        azimut = 0
    elif (dx > 0 and dy == 0):
        azimut = 90
    elif (dx < 0 and dy == 0):
        azimut = 270
    elif (dx == 0 and dy < 0):
        azimut = 180
    elif (dx == 0 and dy > 0):
        azimut = 0

    return azimut

def azimut_classification(azimut: float) -> str:

    """""""""
    Make a classification by azimut value 
    
    Parameters
    ----------
    azimut: float 
        azimut valure in degrees

    Returns
    -------
    classification: str
        return label describing the direction of displacement 
    """""""""

    if ((azimut <= 22.5 and azimut >=0 ) or (azimut <= 360 and azimut > 337.5)):
        classification = 'NORTH'
    elif ((azimut > 22.5 and azimut <= 67.5)):
        classification = 'NORTHEAST'
    elif ((azimut > 67.5 and azimut <= 112.5)):
        classification = 'EAST'
    elif ((azimut > 112.5 and azimut <= 157.5)):
        classification = 'SOUTHEST'
    elif ((azimut > 157.5 and azimut <= 202.5)):
        classification = 'SOUTH'
    elif ((azimut > 202.5 and azimut <= 247.5)):
        classification = 'SOUTHWEST'
    elif ((azimut > 247.5 and azimut <= 292.5)):
        classification = 'WEST'
    elif ((azimut > 292.5 and azimut <= 337.5)):
        classification = 'NORTHWEST'
    return  classification

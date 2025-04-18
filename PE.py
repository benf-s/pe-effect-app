from tkinter import *
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)


import numpy as np
import random as r

import csv, time, threading

# Intializing the tkinter window

window = Tk()
window.title("Photoelectric Effect Simulator")
window.geometry("")
window.configure(bg = "White")


# Global variables
runActive = False
logging = False
vDataRange = []
photocathodeMaterials  = [6.50526,6.0562,2.1965,7.122,7.0382,3.3926]
photonEnergy = 0.0
workFunction = 0.0
maxKE = 0.0
run = True
filepath = ""

# Frames

plotFrame = Frame(window, highlightbackground = "black", highlightthickness=1)
guidedParamFrame = Frame(window, bg="white")
simControlsFrame = Frame(window, bg="white")

# Frame positions

plotFrame.grid(rowspan=2, column=0, padx = 10, pady = 10)
guidedParamFrame.grid(row = 0, column= 1)
simControlsFrame.grid(row = 1, column = 1)

#################################################
################### FUNCTIONS ###################
#################################################

def openHelpWindow():
    # Toplevel object which will
    # be treated as a new window
    helpWindow = Toplevel(window)
 
    # sets the title of the
    # Toplevel widget
    helpWindow.title("Help")
 
    # sets the geometry of toplevel
    helpWindow.geometry("750x450")
 
    # A Label widget to show in toplevel
    Label(helpWindow, text =
    """    Electromagnetic radiation is comprised of photons with energy proportional to the frequency of the radiation. 
    This program simulates the emission of photoelectrons by photons with energy greater than the work function of
    the material upon which they are incident.

    To collect simulated experimental data from this program:
    1) Select photocathode material and incident radiation wavelength. 
    2) Set voltage minimum, maximum and step size for a voltage sweep and press "run simulation".
    3) Adjust voltages and wavelength until the current plot shows the data to be logged.
    4) Click Save As and enter a filename for the data to be written to.
    5) press "Start Logging"; a header will be appended to the file before logged data. The file will
    save in a comma seperated value (.csv) format automatically; an extension need not be specified with the name. 
    6) After you have collected enough runs press "Stop Logging" and repeat for new wavelength settings.
    
    Python application by Ben Fischer-Shane, Department of Physics, Portland State University.
    © 2023 Ben Fischer-Shane. 

    Development of this application was informed by the previous work of Galen Gledhill, Pavel Smejtek, and Erik Bodegom 
    on a similar application for the Portland State University Department of Physics.

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
    as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied 
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License 
    for more details.
""", justify= LEFT).pack()
    
def csvWriter(array):
    with open(filepath, 'a', newline = "") as output:
        writer = csv.writer(output, delimiter= ",")
        writer.writerows(array)

def initiateCSV():
    global logging
    if runActive == True and logging == False and filepath != "":
        csvWriter([[], 
                [], 
                [f"Run on {time.asctime(time.localtime(time.time()))}"], 
                [f"Photocathode: {clicked.get()}"], 
                [f"Wavelength: {wavelengthSlider.get()} Angstroms"],
                ["Voltage (V)", "Current (A)"],
                []]
                )
        log.config(text = "Stop logging", fg = "black")
        logging = True
    elif logging  == True:
        log.config(text = "Start logging", fg = "black")
        logging = False
    

def fileOpen():
    global filepath
    filepath = filedialog.asksaveasfile(mode = "a", title = "Select Log File", defaultextension=".csv", confirmoverwrite = False).name
    if filepath != "":
        clrLog["state"] = "normal"
        if runActive:
            log["state"] = "normal"

def axisLabels():
    graph.set_xlabel("Collector Voltage (Volts)", fontsize = 6)
    graph.set_ylabel("Current (Amps)", fontsize = 6)
    graph.ticklabel_format(style="sci", axis="y", scilimits=(0,0))
    graph.tick_params(axis = "both", labelsize = 8)

def runSim():
    global runActive, run, logging
    # Control the animation
        
    def graphLog():
        global vDataRange, photonEnergy, workFunction, maxKE, runActive
        while run:
            startVoltage=startVoltageSlider.get()
            maxVoltage = maxVoltageSlider.get()
            stepVoltage = stepVoltageSlider.get()
            
            if startVoltage >= maxVoltage:
                stepVoltageLabel.config(fg = "black")
                startVoltageLabel.config(fg = "red")
                stVoltageLabel.config(fg = "red")
                if stepVoltage == 0:
                    stepVoltageLabel.config(fg = "red")
                runPause.config(text = "Run simulation")
                log["state"] = "disabled"
                runActive = False
                break
            elif stepVoltage == 0 or stepVoltage > maxVoltage:
                stVoltageLabel.config(fg="black")
                stVoltageLabel.config(fg = "black")
                stepVoltageLabel.config(fg = "red")
                runPause.config(text = "Run simulation")
                log["state"] = "disabled"
                runActive = False
                break
            
            startVoltageLabel.config(fg="black")
            stVoltageLabel.config(fg = "black")
            stepVoltageLabel.config(fg = "black")

            #The following equations are from a previous photoelectric effect simulator. See credits in "Help" window. 
            vDataRange = np.arange(startVoltage, maxVoltage, stepVoltage)
            photonEnergy = (6.626e3 * 2.9979) / (1.602 *wavelengthSlider.get()) # hc/eL in eV
            workFunction = photocathodeMaterials[clicked.get()-1]

            maxKE = photonEnergy - workFunction/1.488 
            x0 = photonEnergy/(8.625e-5*6000)
            h0 = x0**2/(np.exp(x0)-1)

            x = vDataRange
            y = []
            for i in range(len(x)):
                voltage = vDataRange[i]
                j3 = 0.0
                r1 = r.random()
                r2 = r.random()
                e4 = (-2*np.log(r1))*(0.5-r2)/np.abs(0.5-r2)
                # ~[-20 ...+20]
                j4 = 5e-12*e4        
                if maxKE >0 and voltage <= maxKE:
                    j1 = np.cos(np.pi*voltage/(2*maxKE))
                    r1 = r.random()
                    r2 = r.random()
                    e2 = (-2*0.05*np.log(r1))**2*(0.5-r2)/abs(0.5-r2)
                    j2 = e2*j1
                    j3 = (j1+j2)*h0*1e-6
                y.append(j3+j4) 

                if logging:
                    csvWriter([[voltage, y[i]]])
            if logging:
                csvWriter([[],[]])
            graph.cla()
            axisLabels()
            graph.plot(x, y)
            canvas.draw()
            time.sleep(1)

    # If starting a run
    if runActive == False: 
            run = True
            threading.Thread(target = graphLog).start()
            if filepath != "":
                log["state"] = "normal"
            runPause.config(text = "Pause simulation")

    else:
        runPause.config(text = "Run simulation")
        log.config(text = "Start logging")
        log["state"] = "disabled"
        logging = False
        run = False

    runActive = not runActive




#################################################
################ PLOT SETTINGS ##################
#################################################

# Initializing the plot

fig = Figure(figsize = (4.5, 4)) #orig 3.5 2.5
fig.subplots_adjust(left=0.14, bottom=0.14)

# Adding the subplot and setting blank axes

graph = fig.add_subplot(111)
axisLabels()

# Creating the Tkinter canvas
# Containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master = plotFrame)  
canvas.draw()

# Defining custom toolbar for plot
class activeToolbar(NavigationToolbar2Tk):
    toolitems = (
    ('Home', 'Revert to original view', 'home', 'home'),
    ('Pan', 'Pan view', 'move', 'pan'),
    ('Zoom', 'Zoom', 'zoom_to_rect', 'zoom'),
    ('Save', 'Save plot as image', 'filesave', 'save_figure'),
    ) 
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.label = Label(self, text = "Plot Functions", font=("Arial", 10), bg="gray92")
        self.label.pack(side="left")

# Instantiating the navigation toolbar
toolbar = activeToolbar(canvas, plotFrame)
toolbar.update()

# Placing the canvas on the Tkinter window
canvas.get_tk_widget().pack()


#################################################
########### PARAMETER SELECTION MENU ############
#################################################

# Photocathode dropdown
photocathodeLabel = Label(guidedParamFrame, text= "Select photocathode:", bg="white")
photocathodeLabel.grid(row=0, column=0, sticky="W", padx = 3)
clicked = IntVar(value=1)
photocathodeComboBox = OptionMenu(guidedParamFrame, clicked, *range(1, len(photocathodeMaterials)+1)) # These values are indices of true photocathode material workfunctions, defined in photocathodeMaterials.
photocathodeComboBox.config(bg = "white")
photocathodeComboBox.grid(row=0, column=1, padx=10, sticky = "W", ipady =10)

# Wavelength slider
wavelengthLabel = Label(guidedParamFrame, text="Set wavelength (Å):", bg="white")
wavelengthLabel.grid(row=1, column = 0, sticky="W", padx = 3)
wavelengthSlider = Scale(guidedParamFrame, bg = "white", troughcolor="white", showvalue=True, from_ = 1500, to = 7000, orient="horizontal")
wavelengthSlider.grid(row = 1, column = 1, ipady = 10, padx =10)

# Starting voltage slider
startVoltageLabel = Label(guidedParamFrame, text="Set starting voltage (V):", bg="white")
startVoltageLabel.grid(row=2, column = 0, sticky="W", padx = 3)
startVoltageSlider = Scale(guidedParamFrame, bg = "white", troughcolor="white", showvalue=True, from_ = 0.00, to = 20.00, resolution=0.01, orient="horizontal") 
startVoltageSlider.grid(row = 2, column = 1, ipady = 10, padx =10)

# Step voltage slider
stepVoltageLabel = Label(guidedParamFrame, text="Set step voltage (V):", bg="white")
stepVoltageLabel.grid(row=3, column = 0, sticky="W", padx = 3)
stepVoltageSlider = Scale(guidedParamFrame, bg = "white", troughcolor="white", showvalue=True, from_ = 0.00, to = 0.5, resolution=0.01, orient="horizontal")  
stepVoltageSlider.grid(row = 3, column = 1, ipady = 10, padx =10)

# Max voltage slider
stVoltageLabel = Label(guidedParamFrame, text="Set maximum voltage (V):", bg="white")
stVoltageLabel.grid(row=4, column = 0, sticky="W", padx = 3)
maxVoltageSlider = Scale(guidedParamFrame, bg = "white", troughcolor="white", showvalue=True, from_ = 0.00, to = 20.00, resolution=0.01, orient="horizontal")  
maxVoltageSlider.grid(row = 4, column = 1, padx =10)





#################################################
############# SIMULATION CONTROLS ###############
#################################################

# File name prompt field
filePrompt = Label(simControlsFrame, text="Click Save As and enter the filename to be \n created/appended. Don't include file extension.", bg = "white")
filePrompt.grid(row = 0, column =0, columnspan=2)
fileSave = Button(simControlsFrame, text = "Save As", highlightbackground= "white", command = fileOpen)
fileSave.grid(row = 1, column = 0, columnspan = 2)

# Run/pause simulation button
runPause = Button(simControlsFrame, text="Run simulation", highlightbackground="white", command= runSim) 
runPause.grid(row = 2, column =0 )

# Start/stop logging button
log = Button(simControlsFrame, text="Start logging", highlightbackground="white", command = initiateCSV) 
log["state"] = "disabled"
log.grid(row=2, column = 1 )


# Clear log file button
clrLog = Button(simControlsFrame, text = "Clear log file", highlightbackground="white", command = lambda: open(filepath, "w"))
clrLog["state"] = "disabled"
clrLog.grid(row=3, column = 0)

# Help button
help = Button(simControlsFrame, text="Help", highlightbackground="white", command=openHelpWindow)
help.grid(row=3, column=1)


window.mainloop()

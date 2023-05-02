## BetterBots Project
The BetterBots project is a robot designed to teach coding and engineering concepts. The goal of the Senior Design team at Iowa State is to develop the FPGA portion of the robot.

## Folder Structure
The project's GitHub repository contains the following folders:

root/

├── [Board_Design_Files](Board_Design_Files)/
│   ├── [Active-ADC](Board_Design_Files/Active-ADC/)/
│   ├── [Passive-ADC](Board_Design_Files/Passive-ADC)/
│   ├── [ActiveGerber.zip](Board_Design_Files/ActiveGerber.zip)
│   ├── [PassiveGerber.zip](Board_Design_Files/PassiveGerber.zip)
│   └── [bom.xlsx](Board_Design_Files/bom.xlsx)
├── [Simulation](Simulation)/
│   └── [LTSpice](Simulation/LTSpice)/
└── [Digital_Design_Files](Digital_Design_Files)/
    ├── [orbtrace](Digital_Design_Files/orbtrace/)/
    └── [betterbots.tar](Digital_Design_Files/betterbots.tar)

# Board_Design_Files: 
This folder contains the design files for the board. The files are divided into two subfolders, Active-ADC and Passive-ADC, which contain the active and passive components, respectively. The ActiveGerber.zip and PassiveGerber.zip files contain the Gerber files necessary for manufacturing the board. The bom.xlsx file lists all the components required for the board design.

# Simulation: 
This folder contains the LTSpice simulation files for the project.

# Digital_Design_Files: 
This folder contains the design files for the digital portion of the project. The Orbtrace folder contains the source code for the Orbtrace debugger. The betterbots.tar file contains the code for the BetterBots project.

## Project Details
The project utilizes an ECPIX-5 FPGA to take in multiple types of input devices and apply logic to output the data to another device, such as a Raspberry Pi. This includes an FPGA RISC-v core, Camera subsystem, Fast Fourier Transform, and USB stack. The team envisions executing the project according to the schematic on the right.

The BetterBots project aims to teach coding and engineering concepts through hands-on experimentation with a robot.
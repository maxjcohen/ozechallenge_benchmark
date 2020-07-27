# Oze Challenge Benchmark

[![Build Status](https://dev.azure.com/DanielAtKrypton/Oze%20Challenge%20Benchmark/_apis/build/status/DanielAtKrypton.ozechallenge_benchmark?branchName=master)](https://dev.azure.com/DanielAtKrypton/Oze%20Challenge%20Benchmark/_build/latest?definitionId=1&branchName=master) [![codecov](https://codecov.io/gh/DanielAtKrypton/ozechallenge_benchmark/branch/master/graph/badge.svg)](https://codecov.io/gh/DanielAtKrypton/ozechallenge_benchmark) [![Requirements Status](https://requires.io/github/DanielAtKrypton/ozechallenge_benchmark/requirements.svg?branch=master)](https://requires.io/github/DanielAtKrypton/ozechallenge_benchmark/requirements/?branch=master) [![GitHub license](https://img.shields.io/github/license/DanielAtKrypton/ozechallenge_benchmark)](https://github.com/DanielAtKrypton/ozechallenge_benchmark)

## Table of Contents

1. [Description](#description)
   - 1.1 [Challenge Context](#challenge-context)
   - 1.2 [Challenge Goals](#challenge-goals)
   - 1.3 [Presentation of the challenge at the Collège de France](#presentation-of-the-challenge-at-the-collège-de-france)
   - 1.4 [Data Description](#data-description)
   - 1.5 [Benchmark Description](#benchmark-description)
2. [Requirements](#requirements)
   - 2.1 [Install dependencies](#install-dependencies)
   - 2.2 [Download the dataset](#download-the-dataset)
     - 2.3.1 [Download using credentials (optional)](#download-using-credentials-optional)
3. [Usage](#usage)
4. [Test](#test)

---

## Description

### Challenge context

Oze-Energies is a company specialized in instrumented energy optimization of existing commercial buildings. To achieve this purpose, thousands of communicating sensors, coupled with monitoring and energy optimization software, measure and store a huge number of building-specific data (temperatures, consumptions, etc.) in real time. Using data accumulated for a few weeks and its statistical learning algorithms, Oze-Energies models the energy behavior of each building. Those models then allow identifying and evaluating progress actions for equal comfort which do not require any work, first by acting partly on the settings of climatic equipment (heating, ventilation and air conditioning) and secondly by resizing energy contracts. These actions reduce the energy bill of the owners and tenants by about 25% on average per year.

### Challenge goals

This challenge aims at introducing a new statistical model to predict and analyze energy consumptions and temperatures in a big building using observations stored in the Oze-Energies database. Physics-based approaches to build an energy/temperature simulation tool in order to model complex building behaviors are widespread in the most complex situations. The main drawback of using highly sophisticated software such as TRNsys or EnergyPlus to simulate the behavior of transient systems is the significant computational time required to train such models, as they integrate many noisy sources and a huge number of parameters, and require essentially massive thermodynamics computations. The most common approach is usually either to simplify greatly the model using a schematic understanding of the system, or to run complex time- and resource-consuming campaigns of measurements where trained professionals set the parameters characterizing the physical properties of the system. Even after such campaigns, calibrating these models based on real data obtained from numerous sensors is very difficult. Energy models of buildings depend on a certain number of parameters which influence the accuracy of the simulation. In order to analyze and predict future energy consumptions and future temperatures of a building, it is first necessary to calibrate the model, i.e. find the best parameters to use in the simulation tool so that the model produces similar energy consumptions as the data collected. This usually requires thousands of time-consuming simulations which is not realistic from an industrial point of view. In this data challenge, we propose to build a simplified metamodel to mimic the outputs of the physical model, based on a huge number of stored simulations. The weather conditions are obtained hourly from real sensors to store the real information relative to noisy solicitations of the buildings. The building management system (cooling scheduling, heating scheduling, ventilation scheduling) is chosen by energy managers to provide realistic situations to the physical model. The other unknow parameters characterizing the behavior of the building (air infiltration, capacitance, etc.) are chosen in a grid by energy managers to describe all realistic situations. For each situation specified by these input data, time series of heating and cooling consumptions and of internal temperatures associated with each set of parameters are obtained from the physical model. The objective is to build a simplified energy model and to calibrate this model using the input and output data. This will allow then to use the metamodel to propose new tuned parameters to reduce energy consumptions with a given comfort. The metric considered for the challenge is the MSE (mean squared error).

### Presentation of the challenge at the Collège de France

The presentation of the challenge was made at the Collège de France.

<!-- http://www.college-de-france.fr/video/stephane-mallat/2020/08-sem-mallat-challenge-oze-energies-20200122.mp4 -->

[![Watch the video](https://www.college-de-france.fr/video/stephane-mallat/2020/08-sem-mallat-challenge-oze-energies-20200122_thumb.jpg)](https://player.vimeo.com/video/417838078)

### Data Description

3 datasets are provided as csv files, split between training inputs and outputs, and test inputs.

Input datasets comprise 12116 columns: the first index column contains unique sample identifiers while the other 12115 descriptive features include both information regarding the building itself, which remain constant through time, as well as time series of weather, temperature and occupation information. Each time series includes a month worth of data sampled every hour, i,e, each time series is 28 x 24 = 672 long. More precisely, those input descriptive features correspond to:

- airchange_infiltration_vol_per_h: air changes per hour from ambient,
- capacitance_kJ_perdegreK_perm3: total thermal capacitance of zone air plus that of any mass not considered as walls (e.g. furniture),
- power_VCV_kW_heat: Maximum heating power available,
- power_VCV_kW_clim: Maximum cooling power available,
- nb_occupants: Maximum number of occupants in building,
- nb_PCs: Maximum number of computers in building,
- facade_1_thickness_2: Thickness of insulating layer in facade 1,
- facade_1_window_area_percent: Window surface ratio in facade 1,
- facade_2_thickness_2: Thickness of insulating layer in facade 2,
- facade_2_window_area_percent: Window surface ratio in facade 2,
- facade_3_thickness_2: Thickness of insulating layer in facade 3,
- facade_3_window_area_percent: Window surface ratio in facade 3,
- facade_4_thickness_2: Thickness of insulating layer in facade 4,
- facade_4_window_area_percent: Window surface ratio in facade 4,
- roof_thickness_2: Thickness of the roof,
- ground_thickness_2: Thickness of the ground,
- init_day: First day of simulation,
- init_month: Month of the first day of simulation,
- init_year: Year of simulation,
- ac_t_conf_idh: Comfort temperature of cooling at hour idh of the simulation,
- ac_t_red_idh: Reduced temperature of cooling at hour idh of the simulation,
- ac_mask_idh: Mask describing if air cooling is activated at hour idh of the simulation,
- heat_t_conf_idh: Comfort temperature of heating at hour idh of the simulation,
- heat_t_red_idh: Reduced temperature of heating at hour idh of the simulation,
- heat_mask_idh: Mask describing if heating is activated at hour idh of the simulation
- ventilation_t_idh: Temperature of ventilation at hour idh of the simulation,
- ventilation_vol_idh: Volume of ventilated air at hour idh of the simulation,
- ventilation_mask_idh: Mask describing if ventilation is activated at hour idh of the simulation,
- occupancy_idh: Occupancy profile at hour idh of simulation,
- TAMB_idh: Outside temperatures at hour idh of simulation,

More information on the following weather input data (obtained hourly) can be found at [ammonit.com](https://www.ammonit.com/en/wind-solar-wissen/solarmessung).

- DNI_idh: Direct Normal Irradiance at hour idh,
- RHUM_idh: Humidity at hour idh,
- IBEAM_H_idh: Direct Horizontal Irradiance at hour idh,
- IBEAM_N_idh: Direct Normal Irradiance at hour idh,
- IDIFF_H_idh: Diffuse Horizontal Irradiation at hour idh,
- IGLOB_H_idh: Global Horizontal Irradiance at hour idh,

Output files contain the times series to be predicted hourly from the input. They comprise 5377 columns per sample: the first index column contains the unique sample identifiers (corresponding to the input identifiers) while the other 5376 columns contain the inside temperature of the building and various consumptions in kW/hour, normalized by a factor 2e4 for a better numerical interpretability of the loss:

- T_INT_OFFICE_idh: Inside temperatures,
- Q_AC_OFFICE_idh, Q_HEAT_OFFICE_idh, Q_AHU_C_idh, Q_AHU_H_idh: Cooling, heating and Air handling unit (AHU which can cool or heat outside air) consumptions,
- Q_EQP_idh, Q_LIGHT_idh: PC and Lights consumptions,
- Q_PEOPLE_idh: "Free" heating power due to human activities in the building,

The solution files submitted by participants shall follow this output dataset format (i.e contain the above 5377 columns, where the index values correspond to the input test data). An example submission file containing random predictions is provided.

7500 samples (i.e. lines) are available for the training datasets while 500 observations are used for the test datasets.

### Benchmark Description

Because of the sequential nature of the data, we chose a recurrent neural network as a benchmark. Data: We began by creating our input vectors using, at each time step, both the time series values and the parameters of the building. This amount to an input tensor of shape (672, 37). The input and output values are then normalized to improve convergence of the network. Network: We deployed a simple network in PyTorch, stacking 3 LSTM layers feeding into a fully connected layer. No dropout or batch normalization were applied. Training: We trained the network on the dataset using the mean squared error loss, and the Adam optimizer.

---

## Requirements

- [Install dependencies](#install-dependencies)
- [Download the dataset](#download-the-dataset)
- [Download using credentials (optional)](#download-using-credentials-optional)

### Install dependencies

Clone repository with the following commands in your terminal

#### MacOS or Linux

```bash
git clone https://github.com/maxjcohen/ozechallenge_benchmark.git
cd ozechallenge_benchmark
virtualenv -p python3 .env
. .env/bin/activate
pip install -r requirements/requirements.in
```

#### Windows

```powershell
git clone https://github.com/maxjcohen/ozechallenge_benchmark.git
cd ozechallenge_benchmark
virtualenv -p python3 .env
.\.env\Scripts\activate
pip install -r requirements/requirements.in
```

### Download the dataset

Register if haven't done so yet and login to the challenge [here](https://challengedata.ens.fr/login/?next=/participants/challenges/28/). From there, you have two options to download the dataset:

- log in to the [challenge page](https://challengedata.ens.fr/login/?next=/participants/challenges/28) and download the dataset manually. Place the `.csv` files to `project_root/datasets` folder.
- download the dataset automaticaly using your credentials, see [Download using credentials](#download-using-credentials-optional).

#### Download using credentials (optional)

To allow the automatic download of the challenge data, you have to create a file named `.env.test.local` with the credentials used at [challengedata.ens.fr](https://challengedata.ens.fr/)
Make sure you place this credentials file inside `<project_root>/src/oze_dataset` folder.

It needs to have defined the following environment variables inside:

- CHALLENGE_USER_NAME
- CHALLENGE_USER_PASSWORD

Here is an example of a `.env.test.local` file:

```terminal
CHALLENGE_USER_NAME="your_user_name"
CHALLENGE_USER_PASSWORD="your_password"
```

In the case you want to store your credentials programatically, follow instructions below:

- Create an empty `.env.test.local` file
- Run the following [python-dotenv](https://pypi.org/project/python-dotenv/) commands

```terminal
dotenv -f .env.test.local set CHALLENGE_USER_NAME your_user_name
dotenv -f .env.test.local set CHALLENGE_USER_PASSWORD your_password
```

---

## Usage

Run `benchmark.ipynb`. This file is a Jupyter notebook script that can be run in several different IDE's. To get started with running Jupyter notebooks, follow:.

- ["Working with Jupyter Notebooks in Visual Studio Code"](https://code.visualstudio.com/docs/python/jupyter-support)
- ["Getting started with the classic Jupyter Notebook"](https://jupyter.org/install)

It can also be converted to `benchmark.py` by following the instruction present at the "Debug a Jupyter Notebook" section of ["Working with Jupyter Notebooks in Visual Studio Code"](https://code.visualstudio.com/docs/python/jupyter-support).

---

## Test

In your terminal run pytest at the root folder of the project.

```terminal
pytest
```

---

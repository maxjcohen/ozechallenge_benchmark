Each sample in the dataset is associated with a unique id accross the input and output csv file. It corresponds to a month worth of data sampled every hour, i.e. each time series is 28 x 24 = 672 long. The following is a short description of each variable found in the dataset. A list of these variables, in the same order as saved in the csv file, can be found attached to the challenge.

In the input csv file, we can find information regarding the building itself, which remain constant through time, as well as temperature and occupation as time series. For each sample, we have:
- **id**: a unique identifier (1 column)
- Building parameters:
	- Initial day, month and year as integer (3 columns)
	- General information: **Infiltration**, **Capacitance**, **Heating** and **Cooling Power** (4 columns)
	- Occupancy and usage information: **Number of occupants** and **Number of PCs** (2 columns)
	- Building geometry: **Thickness** and **Window area** for each of the 4 walls, as well as **Thickness** for the roof and ground (10 columns)
- Time series:
	- **Comfort** and **Reduced** heating temperature as well as a **Schedule** (2016 columns)
	- **Comfort** and **Reduced** cooling temperature as well as a **Schedule** (2016 columns)
	- **Ventilation temperature** and **volume** as well as a **Schedule** (2016 columns)
	- **Occupancy** and **Percentage of active PC** (1344 columns)
	- Weather information as time series: **IBEAMH** (Direct Horizontal Irradiance), **IBEAMN** (Direct Normal Irra-diance), **IDIFFH** (Diffuse Horizontal Irradiation), **IGLOBH** (Global Horizontal Irradiance), **RHUM**(humid-ity), **TAMB** (ambiant temperature); More information on these values can be found on [https://www.ammonit.com/en/wind-solar-wissen/solarmessung](https://www.ammonit.com/en/wind-solar-wissen/solarmessung). (4704 columns)

For a total of **12116** columns per sample.

In the output file, we find the same unique identifier along with the inside temperature of the building, and various consumptions in kW/hour, normalized by a factor 2e4 for a better numerical interpretability of the loss: 
- **id**: a unique identifier
- **Inside temperature** (672 columns)
- **Heating and Cooling** consumption for the heater, the AC and the AHU (2688 columns)
- Consumption associated with **People**, **PC** and **Lights** (2016 columns)

For a total of **5377** columns per sample.
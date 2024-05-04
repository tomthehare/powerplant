import React, { useEffect, useState } from "react";

const CurrentConditions = () => {
  // http://192.168.86.172:8000/temperature-samples?location=inside&hours_back=24

  const [loading, setLoading] = useState(true);
  const [currentTemp, setCurrentTemp] = useState(-1);
  const [maxTemp, setMaxTemp] = useState(-1);
  const [minTemp, setMinTemp] = useState(-1);
  const [minTempTs, setMinTempTs] = useState("");
  const [maxTempTs, setMaxTempTs] = useState("");

  useEffect(() => {
    const fetchTemperatureReadings = async () => {
      try {
        const results = await fetch(
          "http://192.168.86.172:8000/temperature-samples?location=inside&hours_back=24"
        );
        const data = await results.json();
        var maxTemp = -1;
        var minTemp = 1000;
        var currentTemp = -1;
        var lastTimestamp = -1;
        var maxTempTs = -1;
        var minTempTs = -1;

        for (let index = 0; index < data.length; index++) {
          const element = data[index];

          if (element["timestamp"] > lastTimestamp) {
            lastTimestamp = element["timestamp"];
            currentTemp = element["temperature"];
          }

          if (element["temperature"] > maxTemp) {
            maxTemp = element["temperature"];
            maxTempTs = element["timestamp"];
          }

          if (element["temperature"] < minTemp) {
            minTemp = element["temperature"];
            minTempTs = element["timestamp"];
          }
        }

        const humanMinTempTime = new Date(minTempTs * 1000);
        const humanMaxTempTime = new Date(maxTempTs * 1000);
        var maxHours = humanMaxTempTime.getHours();
        var minHours = humanMinTempTime.getHours();
        var maxAmPm = "AM";
        var minAmPm = "AM";

        if (humanMinTempTime.getHours() > 12) {
          minHours = humanMinTempTime.getHours() - 12;
          minAmPm = "PM";
        }

        if (humanMaxTempTime.getHours() > 12) {
          maxHours = humanMaxTempTime.getHours() - 12;
          maxAmPm = "PM";
        }

        console.log("max temp ts: " + maxTempTs);
        console.log("max hours: " + humanMaxTempTime.getHours());
        console.log("actual max hours: " + maxHours);

        console.log("min temp ts: " + minTempTs);
        console.log("min hours: " + humanMinTempTime.getHours());
        console.log("actual min hours: " + minHours);

        setCurrentTemp(currentTemp);
        setMaxTemp(maxTemp);
        setMinTemp(minTemp);
        setMaxTempTs(`${maxHours}:${humanMaxTempTime.getMinutes()} ${maxAmPm}`);
        setMinTempTs(`${minHours}:${humanMinTempTime.getMinutes()} ${minAmPm}`);
      } catch (error) {
        console.log("ERROR: ", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTemperatureReadings();
  }, []);

  return loading ? (
    <>
      <h2>LOADING...</h2>
    </>
  ) : (
    <div>
      <div className="container">Current Temperature: {currentTemp}</div>
      <div className="container">
        Min Temperature: {minTemp} ({minTempTs})
      </div>
      <div className="container">
        Max Temperature: {maxTemp} ({maxTempTs})
      </div>
    </div>
  );
};

export default CurrentConditions;

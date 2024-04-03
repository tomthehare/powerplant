import React from "react";
import ReactDOM from "react-dom/client";
import NavBar from "./components/NavBar.tsx";
import "./main.css";
import PowerplantLineGraph from "./components/PowerplantLineGraph.tsx";
import WaterPanel from "./components/WaterPanel.tsx";

const insideData = [
  {
    name: "10:00",
    Temp: 67.3,
    Humidity: 80,
  },
  {
    name: "11:00",
    Temp: 68.9,
    Humidity: 78,
  },
  {
    name: "12:00",
    Temp: 69.8,
    Humidity: 75,
  },
  {
    name: "13:00",
    Temp: 72.2,
    Humidity: 60,
  },
  {
    name: "14:00",
    Temp: 74.1,
    Humidity: 55,
  },
  {
    name: "15:00",
    Temp: 80.0,
    Humidity: 40,
  },
  {
    name: "16:00",
    Temp: 78.2,
    Humidity: 58,
  },
];

const outsideData = [
  {
    name: "10:00",
    Temp: 87.3,
    Humidity: 70,
  },
  {
    name: "11:00",
    Temp: 88.9,
    Humidity: 68,
  },
  {
    name: "12:00",
    Temp: 89.8,
    Humidity: 65,
  },
  {
    name: "13:00",
    Temp: 92.2,
    Humidity: 50,
  },
  {
    name: "14:00",
    Temp: 94.1,
    Humidity: 45,
  },
  {
    name: "15:00",
    Temp: 100.0,
    Humidity: 30,
  },
  {
    name: "16:00",
    Temp: 98.2,
    Humidity: 48,
  },
];

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <NavBar title="powerPLANT" />
    <div className="bodyContent">
      <div className="rowBlock">
        <PowerplantLineGraph data={insideData} title="Inside Conditions" />
        <PowerplantLineGraph data={outsideData} title="Outside Conditions" />
      </div>
      <div className="rowBlock">
        <WaterPanel plantName="Limes" lastOpened="Yesterday" />
      </div>
    </div>
  </React.StrictMode>
);

import EventStackTable from "../components/EventStackTable";
import PowerplantBarChart from "../components/PowerplantBarChart";
import WaterPanel from "../components/WaterPanel";
import PowerplantLineGraph from "../components/PowerplantLineGraph";
import IEvent from "../models/IEvent";
import IPlantGroup from "../models/IPlantGroup";

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

const fanActivity = [
  {
    name: "15:00",
    Minutes: 24,
  },
  {
    name: "16:00",
    Minutes: 55,
  },
  {
    name: "17:00",
    Minutes: 43,
  },
];

const fanEvents: IEvent[] = [
  { date: "Thursday (4/4) at 10:48am", message: "Turned fan on." },
  { date: "Thursday (4/4) at 9:48am", message: "Turned fan off." },
  { date: "Thursday (4/4) at 9:21am", message: "Turned fan on." },
];

const plantGroups: IPlantGroup[] = [
  { description: "Limes", lastWatered: "Yesterday at 2pm" },
  { description: "Peppers", lastWatered: "Yesterday at 3pm" },
  { description: "Tomatoes Zone 1", lastWatered: "Today at 11am" },
  { description: "Beans", lastWatered: "Today at 11am" },
  { description: "Tomatoes Zone 2", lastWatered: "Today at 11am" },
  { description: "Tomatoes Zone 3", lastWatered: "Today at 11am" },
];

const LivePage = () => {
  return (
    <>
      <div className="container">
        <div className="row">
          <div className="col">
            <div className="container-md">
              <PowerplantLineGraph
                data={insideData}
                title="Inside Conditions"
              />
            </div>
          </div>
          <div className="col">
            <div className="container-md">
              <PowerplantLineGraph
                data={outsideData}
                title="Outside Conditions"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="container">
        <div className="row m-5">
          {plantGroups.map((x, index) => {
            return (
              <div key={index} className="col m-3">
                <WaterPanel
                  plantName={x.description}
                  lastOpened={x.lastWatered}
                />
              </div>
            );
          })}
        </div>
      </div>

      <div className="container">
        <div className="row">
          <div className="col col-md-6">
            <PowerplantBarChart title="Fan Activity" data={fanActivity} />
          </div>
          <div className="col col-md-6">
            <EventStackTable eventData={fanEvents} />
          </div>
        </div>
      </div>
    </>
  );
};

export default LivePage;

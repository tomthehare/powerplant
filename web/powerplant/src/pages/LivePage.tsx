import EventStackTable from "../components/EventStackTable";
import PowerplantBarChart from "../components/PowerplantBarChart";
import PowerplantLineGraph from "../components/PowerplantLineGraph";
import PlantGroups from "../components/PlantGroups";

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

const LivePage = () => {
  return (
    <>
      <div className="container">
        <div className="row">
          <div className="col">
            <div className="container">
              <PowerplantLineGraph
                url={
                  "http://192.168.86.172:8000/weather-samples?location=inside"
                }
                title="Inside Conditions"
              />
            </div>
          </div>
        </div>
        <div className="row">
          <div className="col">
            <div className="container pb-4">
              <PowerplantLineGraph
                url={
                  "http://192.168.86.172:8000/weather-samples?location=outside"
                }
                title="Outside Conditions"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="text-center container mt-4">
        <div className="row mt-4">
          <div className="col">
            <h2>Plant Groups</h2>
            <PlantGroups />
          </div>
        </div>
      </div>

      <div className="container">
        <div className="row">
          <div className="col col-md-6">
            <PowerplantBarChart title="Fan Activity" data={fanActivity} />
          </div>
          <div className="col col-md-6">
            <EventStackTable />
          </div>
        </div>
      </div>
    </>
  );
};

export default LivePage;

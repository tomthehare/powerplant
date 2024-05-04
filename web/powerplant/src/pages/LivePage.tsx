import EventStackTable from "../components/EventStackTable";
import PowerplantBarChart from "../components/PowerplantBarChart";
import PowerplantLineGraph from "../components/PowerplantLineGraph";
import PlantGroups from "../components/PlantGroups";
import CurrentConditions from "../components/CurrentConditions";
import EventPanel from "../components/EventPanel";

// const fanActivity = [
//   {
//     name: "15:00",
//     Minutes: 24,
//   },
//   {
//     name: "16:00",
//     Minutes: 55,
//   },
//   {
//     name: "17:00",
//     Minutes: 43,
//   },
// ];

const LivePage = () => {
  return (
    <>
      <div className="container border border-2 border-secondary rounded pb-5 mt-4 text-center ">
        <h2 className="pt-2">Conditions</h2>
        <div className="container">
          <CurrentConditions />
        </div>
        <div className="container mt-4">
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
          {/* <div className="row">
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
        </div> */}
        </div>
      </div>

      <div className="text-center container mt-5 p-1 border border-2 border-secondary rounded">
        <div className="row mt-4">
          <div className="col">
            <h2>Plant Groups</h2>
            <PlantGroups />
          </div>
        </div>
      </div>

      <div className="container text-center mt-5 p-1 border rounded border-2 border-secondary">
        <h2>Events</h2>
        <div className="row justify-content-md-center mt-4">
          {/* <div className="col col-md-6">
            <PowerplantBarChart title="Fan Activity" data={fanActivity} />
          </div> */}
          <div className="col col-md-6">
            <EventPanel />
          </div>
        </div>
      </div>
    </>
  );
};

export default LivePage;

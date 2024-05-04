import { useEffect, useState } from "react";
import WaterPanel from "./WaterPanel";
import IPlantGroup from "../models/IPlantGroup";

const PlantGroups = () => {
  const [plantGroups, setPlantGroups] = useState<Array<IPlantGroup>>([]);
  const [loading, setLoading] = useState(true);

  const onWaterClick = (valveID: number, openDuration: number) => {
    const submittable = {
      valve_id: valveID,
      open_duration_seconds: openDuration,
    };

    console.log("Open duration: " + openDuration);
    console.log("Submittable" + JSON.stringify(submittable));

    fetch("http://192.168.86.172:8000/watering-queue", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(submittable),
    });
  };

  useEffect(() => {
    const fetchPlantGroups = async () => {
      try {
        const results = await fetch("http://192.168.86.172:8000/plant-groups");
        const data = await results.json();

        const renderData = [];
        for (let index = 0; index < data.length; index++) {
          const element = data[index];

          renderData.push({
            valveID: element["valve_id"],
            lastWatered: element["last_watered"],
            description: element["description"],
          });
        }

        setPlantGroups(renderData);
      } catch (error) {
        console.log("ERROR: ", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlantGroups();
  }, []);

  return loading ? (
    <h2>LOADING</h2>
  ) : (
    <div className="container">
      <div className="row m-3">
        {plantGroups.map((plantGroup, index) => {
          return (
            <div key={index} className="col m-3">
              <WaterPanel
                plantName={plantGroup.description}
                lastOpened={plantGroup.lastWatered}
                valveID={plantGroup.valveID}
                onWaterClick={onWaterClick}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PlantGroups;

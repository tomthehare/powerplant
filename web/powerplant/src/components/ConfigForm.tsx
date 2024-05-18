import { useEffect, useState } from "react";
import { SubmitHandler, useForm } from "react-hook-form";
import IConfig from "../models/IConfig";
import IPlantGroup from "../models/IPlantGroup";

type FormFields = {
  fanTemperature: number;
  wateringHours: string;
  waterEveryDays: number;
  plantGroups: IPlantGroup[];
};

const ConfigForm = () => {
  /**
   * Set up the necessary state and handlers for the form content
   */
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormFields>();

  const [configStore, setConfigStore] = useState<IConfig | null>(null);
  const [isLoadingConfigStore, setIsLoadingConfigStore] = useState(true);

  /**
   * Load the initial state of the configuration
   */
  useEffect(() => {
    const getConfigStore = async () => {
      try {
        const config = await fetch("http://192.168.86.172:8000/config");
        const configDict = await config.json();

        const plantGroups = [];
        for (
          let index = 0;
          index < configDict["plant_groups"].length;
          index++
        ) {
          const element = configDict["plant_groups"][index];
          plantGroups.push({
            valveID: element["valve_id"],
            description: element["description"],
            lastWatered: element["last_watered"],
            openDurationSeconds: element["open_duration_seconds"],
          });
        }

        var tempConfigStore: IConfig = {
          fanTemperature: configDict["fan_temperature"],
          waterConfig: {
            waterEveryDays: configDict["water_config"]["water_every_days"],
            hours: configDict["water_config"]["hours"],
          },
          plantGroups: plantGroups,
        };

        setConfigStore(tempConfigStore);
      } catch (error) {
        console.log(error);
      } finally {
        setIsLoadingConfigStore(false);
      }
    };

    getConfigStore();
  }, []);

  /**
   * Set up the submit handler.  Unfortunately the python api and the types in here aren't exactly equivalent, so there is
   * some mapping work to be done.
   *
   * @param data Data coming from the form, as part of the registered hooks
   */
  const onSubmit: SubmitHandler<FormFields> = async (data) => {
    try {

      const plantGroups = [];
      for (let index = 0; index < data.plantGroups.length; index++) {
        plantGroups.push({
          valve_id: data.plantGroups[index].valveID,
          description: data.plantGroups[index].description,
          open_duration_seconds: data.plantGroups[index].openDurationSeconds,
        });
      }

      const submittable = {
        fan_temperature: data.fanTemperature,
        water_config: {
          hours: data.wateringHours.split(","),
          water_every_days: data.waterEveryDays,
        },
        // plant_groups: configStore?.plantGroups,
        plant_groups: plantGroups
      };

      await fetch("http://192.168.86.172:8000/config", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(submittable),
      });
    } catch (error) {
      setError("root", { message: "something bad happened: " + error });
    }
  };

  /**
   * Start the render part of the component
   */
  return isLoadingConfigStore ? (
    <h2>LOADING</h2>
  ) : (
    <>
      {console.log(configStore)}
      <div className="container">
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="row">
            <div className="col">
              <h3>Fan</h3>
              <span>Fan Temperature: </span>
              <input
                {...register("fanTemperature", {
                  pattern: {
                    value: /^\d+$/,
                    message: "Temperature must be numeric.",
                  },
                  required:
                    "You must provide a fan temp or else plants will die.",
                })}
                type="text"
                defaultValue={configStore?.fanTemperature}
              />
              {errors.fanTemperature && (
                <div className="text-danger">
                  {errors.fanTemperature.message}
                </div>
              )}
              <br />
            </div>
          </div>
          <div className="row">
            <div className="col">
              <h3>Watering</h3>
              <span>Watering Hours (comma-separated): </span>
              <input
                {...register("wateringHours")}
                type="text"
                defaultValue={configStore?.waterConfig.hours.join(",")}
              />
              <br />
              <span>Water every days: </span>
              <input
                {...register("waterEveryDays")}
                type="number"
                defaultValue={
                  configStore != null
                    ? String(configStore?.waterConfig.waterEveryDays)
                    : "1"
                }
              />
            </div>
          </div>
          <div className="row">
            <div className="col">

              {/* START OF VALVES!!!! */}

            </div>
          </div>
          <div className="row">
            <div className="col">
              <h3>Valves</h3>
            </div>
          </div>
          <div className="row">
            <div className="col">
              <h4>Valve 1</h4>
              <input
                type="hidden"
                {...register("plantGroups.0.valveID")}
                value={configStore?.plantGroups[0].valveID}
              />
              <span>Name: </span>
              <input
                {...register("plantGroups.0.description")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[0].description)
                    : ""
                }
              />
              <br />
              <span>Open duration seconds: </span>
              <input
                {...register("plantGroups.0.openDurationSeconds")}
                type="number"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[0].openDurationSeconds)
                    : ""
                }
              />
            </div>
          </div>
          <div className="row">
            <div className="col">
              <br />

              <h4>Valve 2</h4>
              <input
                type="hidden"
                {...register("plantGroups.1.valveID")}
                value={configStore?.plantGroups[1].valveID}
              />
              <span>Name: </span>
              <input
                {...register("plantGroups.1.description")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[1].description)
                    : ""
                }
              />
              <br />
              <span>Open duration seconds: </span>
              <input
                {...register("plantGroups.1.openDurationSeconds")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[1].openDurationSeconds)
                    : ""
                }
              />
            </div>
          </div>
          <div className="row">
            <div className="col">
              <br />

              <h4>Valve 3</h4>
              <input
                type="hidden"
                {...register("plantGroups.2.valveID")}
                value={configStore?.plantGroups[2].valveID}
              />
              <span>Name: </span>
              <input
                {...register("plantGroups.2.description")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[2].description)
                    : ""
                }
              />
              <br />
              <span>Open duration seconds: </span>
              <input
                {...register("plantGroups.2.openDurationSeconds")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[2].openDurationSeconds)
                    : ""
                }
              />
            </div>
          </div>
          <div className="row">
            <div className="col">
              <br />

              <h4>Valve 4</h4>
              <input
                type="hidden"
                {...register("plantGroups.3.valveID")}
                value={configStore?.plantGroups[3].valveID}
              />
              <span>Name: </span>
              <input
                {...register("plantGroups.3.description")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[3].description)
                    : ""
                }
              />
              <br />
              <span>Open duration seconds: </span>
              <input
                {...register("plantGroups.3.openDurationSeconds")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[3].openDurationSeconds)
                    : ""
                }
              />
            </div>
          </div>
          <div className="row">
            <div className="col">
              <br />

              <h4>Valve 5</h4>
              <input
                type="hidden"
                {...register("plantGroups.4.valveID")}
                value={configStore?.plantGroups[4].valveID}
              />
              <span>Name: </span>
              <input
                {...register("plantGroups.4.description")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[4].description)
                    : ""
                }
              />
              <br />
              <span>Open duration seconds: </span>
              <input
                {...register("plantGroups.4.openDurationSeconds")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[4].openDurationSeconds)
                    : ""
                }
              />
            </div>
          </div>
          <div className="row">
            <div className="col">
              <br />

              <h4>Valve 6</h4>
              <input
                type="hidden"
                {...register("plantGroups.5.valveID")}
                value={configStore?.plantGroups[5].valveID}
              />
              <span>Name: </span>
              <input
                {...register("plantGroups.5.description")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[5].description)
                    : ""
                }
              />
              <br />
              <span>Open duration seconds: </span>
              <input
                {...register("plantGroups.5.openDurationSeconds")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[5].openDurationSeconds)
                    : ""
                }
              />
            </div>
          </div>
          <div className="row">
            <div className="col">
              <br />

              <h4>Valve 7</h4>
              <input
                type="hidden"
                {...register("plantGroups.6.valveID")}
                value={configStore?.plantGroups[6].valveID}
              />
              <span>Name: </span>
              <input
                {...register("plantGroups.6.description")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[6].description)
                    : ""
                }
              />
              <br />
              <span>Open duration seconds: </span>
              <input
                {...register("plantGroups.6.openDurationSeconds")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[6].openDurationSeconds)
                    : ""
                }
              />
            </div>
          </div>
          <div className="row">
            <div className="col">
              <br />

              <h4>Valve 8</h4>
              <input
                type="hidden"
                {...register("plantGroups.7.valveID")}
                value={configStore?.plantGroups[7].valveID}
              />
              <span>Name: </span>
              <input
                {...register("plantGroups.7.description")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[7].description)
                    : ""
                }
              />
              <br />
              <span>Open duration seconds: </span>
              <input
                {...register("plantGroups.7.openDurationSeconds")}
                type="string"
                defaultValue={
                  configStore != null
                    ? String(configStore?.plantGroups[7].openDurationSeconds)
                    : ""
                }
              />

              <br />
            </div>
          </div>
          <div className="row mt-4">
            <div className="col">
              <button
                className="btn btn-primary"
                type="submit"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Waiting..." : "Submit Changes"}
              </button>
              {errors.root && (
                <div className="text-danger">{errors.root.message}</div>
              )}
            </div>
          </div>
        </form>
      </div>
    </>
  );
};

export default ConfigForm;

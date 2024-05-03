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

        var tempConfigStore: IConfig = {
          fanTemperature: configDict["fan_temperature"],
          waterConfig: {
            waterEveryDays: configDict["water_config"]["water_every_days"],
            hours: configDict["water_config"]["hours"],
          },
          plantGroups: configDict["plant_groups"],
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
      const submittable = {
        fan_temperature: data.fanTemperature,
        water_config: {
          hours: data.wateringHours.split(","),
          water_every_days: data.waterEveryDays,
        },
        plant_groups: configStore?.plantGroups,
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

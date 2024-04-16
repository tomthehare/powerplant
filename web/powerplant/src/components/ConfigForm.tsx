import { useEffect, useState } from "react";
import { SubmitHandler, useForm } from "react-hook-form";
import IConfig from "../models/IConfig";

type FormFields = {
  fanTemperature: number;
  wateringHours: string;
};

const ConfigForm = () => {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormFields>();

  const [configStore, setConfigStore] = useState<IConfig | null>(null);
  const [isLoadingConfigStore, setIsLoadingConfigStore] = useState(true);
  useEffect(() => {
    const getConfigStore = async () => {
      try {
        const config = await fetch("http://localhost:8000/config");
        const configDict = await config.json();

        var tempConfigStore: IConfig = {
          fanTemperature: configDict["fan_temperature"],
          waterConfig: {
            waterEveryDays: 1,
            hours: [7],
          },
          plantGroups: [],
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

  const onSubmit: SubmitHandler<FormFields> = async (data) => {
    try {
      const submittable = {
        fan_temperature: data.fanTemperature,
        water_config: {
          hours: data.wateringHours.split(","),
          water_every_days: 0,
        },
        plant_groups: [],
      };

      const updateResults = await fetch("http://localhost:8000/config", {
        method: "PATCH",
      });
    } catch (error) {
      setError("root", { message: "something bad happened" });
    }
  };

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
              <span>Watering Hours: </span>
              <input
                {...register("wateringHours")}
                type="text"
                defaultValue={configStore?.waterConfig.hours.join(",")}
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

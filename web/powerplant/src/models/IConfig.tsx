import IPlantGroup from "./IPlantGroup";

interface IConfig {
  fanTemperature: number;
  waterConfig: IWaterConfig;
  plantGroups: IPlantGroup[];
}

export default IConfig;

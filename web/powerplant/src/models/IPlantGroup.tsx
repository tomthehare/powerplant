interface IPlantGroup {
  valveID: number;
  description: string;
  lastWatered: string;
  openDurationSeconds: number;
  pumpModulationHalfCycleSeconds: number;
}

export default IPlantGroup;

interface WaterPanelProps {
  plantName: string;
  lastOpened: string;
}

const WaterPanel = ({ plantName, lastOpened }: WaterPanelProps) => {
  return (
    <>
      <div className="rowBlock">{plantName}</div>
      <div className="rowBlock">{lastOpened}</div>
      <div className="rowBlock">
        <button>Water</button>
      </div>
    </>
  );
};

export default WaterPanel;

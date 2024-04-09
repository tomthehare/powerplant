interface WaterPanelProps {
  plantName: string;
  lastOpened: string;
}

const WaterPanel = ({ plantName, lastOpened }: WaterPanelProps) => {
  return (
    <>
      <div className="container m-2 border rounded">
        <div className="row fw-bold text-center">
          <div className="col">{plantName}</div>
        </div>
        <div className="row text-center">
          <div className="col">{lastOpened}</div>
        </div>
        <div className="row m-2">
          <div className="col text-center">
            <button className="btn btn-primary">Water</button>
          </div>
        </div>
      </div>
    </>
  );
};

export default WaterPanel;

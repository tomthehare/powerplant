interface WaterPanelProps {
  plantName: string;
  lastOpened: string;
  valveID: number;
  onWaterClick: (valveID: number, openDurationSeconds: number) => void;
}

const WaterPanel = ({
  plantName,
  lastOpened,
  valveID,
  onWaterClick,
}: WaterPanelProps) => {
  var lastOpenedString: string | null = null;

  if (lastOpened != null) {
    var seconds: number = +lastOpened;

    // Need to format the last opened timestamp to be how we want it.
    const days = Math.floor(seconds / 86400);
    seconds = seconds - days * 86400;
    const hours = Math.floor(seconds / 3600);
    seconds = seconds - hours * 3600;
    const minutes = Math.floor(seconds / 60);
    seconds = seconds - minutes * 60;

    var delta_pieces: string[] = [];

    if (days > 0) {
      delta_pieces.push(`${days} days`);
    }

    if (hours > 0) {
      delta_pieces.push(`${hours} hours`);
    }

    if (minutes > 0) {
      delta_pieces.push(`${minutes} minutes`);
    }

    if (seconds > 0) {
      delta_pieces.push(`${seconds} seconds`);
    }

    lastOpenedString = delta_pieces.join(" ");
  }

  return (
    <>
      <div className="container m-2 p-3 border rounded">
        <div className="row fw-bold text-center">
          <div className="col">{plantName}</div>
        </div>
        <div className="row text-center">
          <div className="col">
            Last watered:{" "}
            {lastOpenedString == null ? "never" : lastOpenedString}
          </div>
        </div>
        <div className="row m-2">
          <div className="col text-center">
            <button
              className="btn btn-primary"
              onClick={() => {
                onWaterClick(valveID, 20);
              }}
            >
              Water
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default WaterPanel;

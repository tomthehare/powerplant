import React from "react";
import EventStackTable from "./EventStackTable";

const EventPanel = () => {
  return (
    <>
      <div className="container border rounded">
        <div className="row">
          <div className="col">
            <button className="btn btn-primary m-3">Fans</button>
            <button className="btn btn-primary m-3">Valves</button>
            <button className="btn btn-primary m-3">Windows</button>
          </div>
        </div>
        <div className="row">
          <div className="col">
            <EventStackTable eventType="all" />
          </div>
        </div>
      </div>
    </>
  );
};

export default EventPanel;

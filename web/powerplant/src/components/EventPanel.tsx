import React, { useState } from "react";
import EventStackTable from "./EventStackTable";

const EventPanel = () => {
  const [eventTypeFilter, setEventTypeFilter] = useState("all");

  return (
    <>
      <div className="container border rounded">
        <div className="row">
          <div className="col">
            <button
              className="btn btn-primary m-3"
              onClick={() => {
                setEventTypeFilter("fan");
              }}
            >
              Fans
            </button>
            <button
              className="btn btn-primary m-3"
              onClick={() => {
                setEventTypeFilter("valve");
              }}
            >
              Valves
            </button>
            <button
              className="btn btn-primary m-3"
              onClick={() => {
                setEventTypeFilter("window");
              }}
            >
              Windows
            </button>
          </div>
        </div>
        <div className="row">
          <div className="col">
            <EventStackTable eventType={eventTypeFilter} />
          </div>
        </div>
      </div>
    </>
  );
};

export default EventPanel;

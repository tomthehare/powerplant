import { useEffect, useState } from "react";
import IEvent from "../models/IEvent";

interface EventStackTableProps {
  eventType: string;
}

const EventStackTable = ({ eventType = "all" }: EventStackTableProps) => {
  const [events, setEvents] = useState<Array<IEvent>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const results = await fetch(
          "http://192.168.86.172:8000/events?type=" + eventType
        );
        const data = await results.json();

        const humanData = [];
        for (let index = 0; index < data.length; index++) {
          const element = data[index];

          const humanMessage =
            element.subject_type +
            " " +
            element.subject_id +
            " " +
            element.verb;
          const humanDate = new Date(element.timestamp * 1000);

          const year = humanDate.getFullYear();
          const month = (humanDate.getMonth() + 1).toString().padStart(2, "0"); // Months are zero-indexed in JavaScript
          const day = humanDate.getDate().toString().padStart(2, "0");
          var hours = humanDate.getHours();
          const minutes = humanDate.getMinutes().toString().padStart(2, "0");

          var amPm = "AM";
          if (hours > 12) {
            hours = hours - 12;
            amPm = "PM";
          }

          const hoursString = hours.toString().padStart(2, "0");

          // Format the date as a string
          const humanDateString = `${year}-${month}-${day} ${hoursString}:${minutes} ${amPm}`;

          humanData.push({
            message: humanMessage,
            date: humanDateString,
          });
        }

        setEvents(humanData);
      } catch (error) {
        console.log("ERROR: ", error);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  return loading ? (
    <div className="container">
      <h2>LOADING</h2>
    </div>
  ) : (
    <div className="table-responsive">
      <table className="table table-dark">
        <thead>
          <tr>
            <th scope="col">Date</th>
            <th scope="col">Message</th>
          </tr>
        </thead>
        <tbody>
          {events.map((x, index) => {
            return (
              <tr key={index}>
                <td>{x.date}</td>
                <td>{x.message}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default EventStackTable;

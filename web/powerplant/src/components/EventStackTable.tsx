import IEvent from "../models/IEvent";

interface EventStackTableProps {
  eventData: IEvent[];
}

const EventStackTable = ({ eventData }: EventStackTableProps) => {
  return (
    <div className="table-responsive">
      <table className="table table-dark">
        <thead>
          <tr>
            <th scope="col">Date</th>
            <th scope="col">Message</th>
          </tr>
        </thead>
        <tbody>
          {eventData.map((x, index) => {
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

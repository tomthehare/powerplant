import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import IWeatherSample from "../models/IWeatherSample";

interface PowerplantLineGraphProps {
  url: string;
  title: string;
}

const PowerplantLineGraph = ({ url, title }: PowerplantLineGraphProps) => {
  const [data, setData] = useState<Array<IWeatherSample>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const results = await fetch(url);
        const data = await results.json();

        console.log(data);

        var humanData = [];
        for (let index = 0; index < data.length; index++) {
          const element = data[index];

          const humanDate = new Date(element.timestamp * 1000);

          var hours = ("0" + humanDate.getHours()).slice(-2);
          const minutes = ("0" + humanDate.getMinutes()).slice(-2);

          // Format the date as a string
          const humanDateString = `${hours}:${minutes}`;

          humanData.push({
            timestamp: humanDateString,
            temperature: element.temperature,
            humidity: element.humidity,
          });
        }

        setData(humanData);
      } catch (error) {
        console.log("ERROR: ", error);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  return loading ? (
    <>
      <h2>loading</h2>
    </>
  ) : (
    <>
      <div className="graphDiv text-center fs-5 mt-5">
        <div className="fw-bold">{title}</div>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="temperature"
              stroke="#8884d8"
              activeDot={{ r: 1 }}
            />
            <Line
              type="monotone"
              dataKey="humidity"
              stroke="#82ca9d"
              activeDot={{ r: 1 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default PowerplantLineGraph;

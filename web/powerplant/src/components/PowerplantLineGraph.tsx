import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface PowerplantLineGraphProps {
  data: Array<Object>;
  title: string;
}

const PowerplantLineGraph = ({ data, title }: PowerplantLineGraphProps) => {
  return (
    <>
      <div className="chartDiv">
        <div className="chartTitle">{title}</div>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="Temp"
              stroke="#8884d8"
              activeDot={{ r: 1 }}
            />
            <Line
              type="monotone"
              dataKey="Humidity"
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

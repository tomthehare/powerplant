import {
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
} from "recharts";

interface PowerplantBarChartProps {
  data: Array<Object>;
  title: string;
}

const PowerplantBarChart = ({ data, title }: PowerplantBarChartProps) => {
  return (
    <>
      <div className="barChartDiv text-center fs-5 mt-5">
        <div className="fw-bold">{title}</div>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            width={500}
            height={400}
            data={data}
            margin={{
              top: 20,
              right: 20,
              bottom: 20,
              left: 20,
            }}
          >
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="amt"
              fill="#8884d8"
              stroke="#8884d8"
            />
            <Bar dataKey="Minutes" barSize={20} fill="#413ea0" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default PowerplantBarChart;

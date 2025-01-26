import { useEffect, useRef } from "react";
import Plotly from 'plotly.js-dist';
import "./ChatBot.css";
import { VisualizationProps } from "../../interfaces/visualizationProps"; "./../../interfaces/visualizationProps"


const Visualization = ({ data, layout, }: VisualizationProps) => {
  const chartRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (chartRef.current) {
      Plotly.purge(chartRef.current);
    }

    const chartLayout = {
      ...layout,
      autosize: true,
      responsive: true,
      width: 850,
      height: 400
    };

    setTimeout(() => {
      if (chartRef.current) {
        Plotly.newPlot(chartRef.current, data, chartLayout);
        Plotly.Plots.resize(chartRef.current, data, chartLayout);
      }
    }, 0);

  
  }, [data, layout]);

  useEffect(() => {
    const chartLayout = {
      ...layout,
      autosize: true,
      responsive: true,
      width: 850 ,
      height: 400
    };
    if (chartRef.current) {
      Plotly.Plots.resize(chartRef.current, data, chartLayout);
    }
  }, []);

  return <div ref={chartRef} style={{ width: "100%", height: "100%" }} />;
};

export default Visualization;

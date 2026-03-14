import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import type { TrendPoint } from '../types'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
)

interface Props {
  points: TrendPoint[]
  label?: string
}

export default function PriceTrendChart({ points, label = 'Avg USD Price' }: Props) {
  if (points.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
        No trend data available
      </div>
    )
  }

  const data = {
    labels: points.map((p) => p.date),
    datasets: [
      {
        label,
        data: points.map((p) => p.avg_usdprice),
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37,99,235,0.1)',
        borderWidth: 2,
        pointRadius: 2,
        tension: 0.3,
        fill: true,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx: { raw: unknown }) => `$${Number(ctx.raw).toFixed(2)}`,
        },
      },
    },
    scales: {
      y: {
        ticks: { callback: (v: unknown) => `$${Number(v).toFixed(2)}` },
      },
    },
  }

  return (
    <div className="h-48">
      <Line data={data} options={options} />
    </div>
  )
}

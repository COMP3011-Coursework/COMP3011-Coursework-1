import type { VolatilityItem } from '../types'

interface Props {
  items: VolatilityItem[]
}

export default function VolatilityList({ items }: Props) {
  if (items.length === 0) {
    return <p className="text-gray-400 text-sm">No data</p>
  }

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-left text-gray-500 border-b border-gray-200">
          <th className="pb-1 font-medium">Commodity</th>
          <th className="pb-1 font-medium text-right">CV</th>
          <th className="pb-1 font-medium text-right">Avg USD</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.commodity_id} className="border-b border-gray-100 last:border-0">
            <td className="py-1 truncate max-w-[140px]">{item.commodity_name}</td>
            <td className="py-1 text-right font-mono">{item.cv.toFixed(3)}</td>
            <td className="py-1 text-right font-mono">${item.avg_usdprice.toFixed(2)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

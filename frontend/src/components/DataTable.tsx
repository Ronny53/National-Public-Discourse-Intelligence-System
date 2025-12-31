interface Column<T> {
  key: keyof T | string
  label: string
  width?: string
  render?: (row: T) => React.ReactNode
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyField: keyof T
}

export default function DataTable<T>({ columns, data, keyField }: DataTableProps<T>) {
  const getCellValue = (row: T, column: Column<T>) => {
    if (column.render) {
      return column.render(row)
    }
    const key = column.key as keyof T
    return row[key] as React.ReactNode
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr>
            {columns.map((col) => (
              <th 
                key={col.key as string} 
                className="table-header"
                style={{ width: col.width }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr 
              key={String(row[keyField])} 
              className="hover:bg-surface-elevated transition-colors"
            >
              {columns.map((col) => (
                <td key={col.key as string} className="table-cell">
                  {getCellValue(row, col)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

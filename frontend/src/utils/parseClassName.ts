export function parseClassName(className: string): { crop: string, condition: string } {
  if (!className) {
    return { crop: "Unknown", condition: "Unknown" }
  }
  const parts = className.split('___')
  if (parts.length === 2) {
    const crop = parts[0].replace(/_/g, ' ')
    const condition = parts[1].replace(/_/g, ' ')
    return { crop, condition }
  }
  return { crop: "Unknown", condition: className.replace(/_/g, ' ') }
}

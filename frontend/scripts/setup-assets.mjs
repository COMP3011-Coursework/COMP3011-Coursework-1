import { existsSync, mkdirSync, writeFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const DEST = join(ROOT, 'public', 'data', 'world.geojson')
const URL  = 'https://raw.githubusercontent.com/datasets/geo-countries/main/data/countries.geojson'

if (existsSync(DEST)) {
  process.exit(0)
}

console.log('Downloading world.geojson…')
mkdirSync(join(ROOT, 'public', 'data'), { recursive: true })

const res = await fetch(URL)
if (!res.ok) throw new Error(`Failed to download GeoJSON: ${res.status} ${res.statusText}`)

const buf = await res.arrayBuffer()
writeFileSync(DEST, Buffer.from(buf))
console.log('world.geojson saved.')

import countries from 'i18n-iso-countries'
import en from 'i18n-iso-countries/langs/en.json'

countries.registerLocale(en)

export function countryName(iso3: string): string {
  return countries.getName(iso3, 'en') ?? iso3
}

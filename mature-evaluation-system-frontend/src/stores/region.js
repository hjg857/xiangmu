// /stores/region.js
import { defineStore } from 'pinia'

export const useRegionStore = defineStore('region', {
  state: () => ({
  currentRegion: JSON.parse(localStorage.getItem('region') || 'null')
}),
actions: {
  setRegion(region) {
    this.currentRegion = region
    localStorage.setItem('region', JSON.stringify(region))
  }
}
})
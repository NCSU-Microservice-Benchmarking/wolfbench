export interface image {
  id: string,
  type: string,
  name: string,
  url: string,
  base64: string
} 

export interface models {
  [task: string]: {
    short_name: string,
    long_name: string,
    description: string,
    icon?: string,
    models: {
      name: string,
      path: string,
      img?: string
    }[]
  }
}

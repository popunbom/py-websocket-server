export type Message = {
  body: string
  timestamp: string
}


export function isMessage(obj: any): obj is Message {
  return typeof obj === "object"
    && typeof obj.body === "string"
    && typeof obj.timestamp === "string"
}

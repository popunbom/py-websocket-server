type DataURLEncoding = "plain" | "base64"
type DataURL = {
  media_type: string
  encoding: DataURLEncoding
  data: string
}

function isDataURL(obj: any): obj is DataURL {
  return typeof obj === "object"
    && typeof obj.media_type === "string"
    && (
      typeof obj.encoding === "string"
      && (obj.encoding === "plain" || obj.encoding === "base64")
    )
    && typeof obj.data === "string"
}

type MessageType = "text" | "voice"
type MessageBody = {
  type: MessageType
  content: string | DataURL
}
function isMessageBody(obj: any): obj is MessageBody {
  return typeof obj === "object"
    && (
      typeof obj.type === "string"
      && (obj.type === "text" || obj.type === "voice")
    )
    && (
      typeof obj.content === "string"
      || isDataURL(obj)
    )
}

const dateNow = (): string => (new Date()).toISOString()

export class Message {
  body: MessageBody
  timestamp: string

  constructor(body: MessageBody, timestamp: string) {
    this.body = body
    this.timestamp = timestamp
  }

  text(): string {
    if (typeof this.body.content === "string") {
      return this.body.content
    }
    else if (this.body.type === "voice") {
      return "**voice-data**"
    }
    return "undefined"
  }

  timestampToString(): string {
    const d = (new Date(Date.parse(this.timestamp)))
    d.setHours(d.getHours())
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`
  }

  static fromPlainText(text: string): Message {
    return new Message(
      { type: "text", content: text },
      dateNow(),
    )
  }
  static fromVoiceDataURL(dataUrl: string): Message | null {
    const ENCODING_MAP = <{ [key: string]: DataURLEncoding }>{
      "": "plain",
      "base64": "base64"
    }
    const [header, body] = dataUrl.split(",", 2)
    const match = header.match(/^data:(?<media_type>[^;]*)(?:;(?<encoding>.*))*$/)
    if (match === null) {
      return null
    }
    return new Message(
      {
        type: "voice",
        content: {
          media_type: match.groups?.media_type || "",
          encoding: ENCODING_MAP[match.groups?.encoding || ""],
          data: body
        } as DataURL
      },
      dateNow(),
    )
  }
}
export function isMessage(obj: any): obj is Message {
  return typeof obj === "object"
    && isMessageBody(obj.body)
    && typeof obj.timestamp === "string"
}

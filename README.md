# earthquake-notify

Send earthquake-related notifications to Discord and Twitter.

## Function

- Receiving and notifying Earthquake Early Warnings using a strong motion monitor
- Acquisition and notification of earthquake information from the Japan Meteorological Agency
- Acquisition and notification of NHK earthquake information and map images

## Flow

### When an earthquake occurs

- Receive Earthquake Early Warning from strong motion monitor and send to Discord / Twitter

### When earthquake information is released by the Japan Meteorological Agency

- Process the published content and send it to Discord / Twitter

### NHKによる地震情報公開時

- Process the published content and send it to Discord / Twitter

## Config

- `discord`: Discord notification settings
  - `token`: Bot token (String)
  - `channel`: Global Channel ID (String)
  - `webhook_url`: Global WebHook URL (String)
  - `early`: Settings for Earthquake Early Warning
    - `enable`: Is Enable (Boolean)
    - `channel`: Channel ID (String)
    - `webhook_url`: WebHook URL (String)
  - `jma`: Settings related to earthquake information by the Japan Meteorological Agency
    - `enable`: Is Enable (Boolean)
    - `channel`: Channel ID (String)
    - `webhook_url`: WebHook URL (String)
  - `nhk`: Settings related to earthquake information by NHK
    - `enable`: Is Enable (Boolean)
    - `channel`: Channel ID (String)
    - `webhook_url`: WebHook URL (String)
- `twitter`: Settings related to Twitter notifications
  - `consumer_key`: Global Consumer Key (String)
  - `consumer_secret`: Global Consumer Secret (String)
  - `access_token`: Global Access Token (String)
  - `access_token_secret`: Global Access Token Secret (String)
  - `early`: Settings for Earthquake Early Warning
    - `consumer_key`: Consumer Key (String)
    - `consumer_secret`: Consumer Secret (String)
    - `access_token`: Access Token (String)
    - `access_token_secret`: Access Token Secret (String)
  - `jma`: Settings related to earthquake information by the Japan Meteorological Agency
    - `consumer_key`: Consumer Key (String)
    - `consumer_secret`: Consumer Secret (String)
    - `access_token`: Access Token (String)
    - `access_token_secret`: Access Token Secret (String)
  - `nhk`: Settings related to earthquake information by NHK
    - `consumer_key`: Consumer Key (String)
    - `consumer_secret`: Consumer Secret (String)
    - `access_token`: Access Token (String)
    - `access_token_secret`: Access Token Secret (String)

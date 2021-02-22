# earthquake-notify

地震関連の通知をDiscordとTwitterに送信します。

## Function

- 強震モニタを使った緊急地震速報の受信・通知
- 気象庁の地震情報の取得・通知
- NHKの地震情報・地図画像の取得・通知

## Flow

### 地震発生時

- 緊急地震速報を強震モニタから受け取り、Discord・Twitterに送信する

### 気象庁による地震情報公開時

- 公開内容を加工し、Discord・Twitterに送信する

### NHKによる地震情報公開時

- 公開内容を加工し、Discord・Twitterに送信する

## Config

- `discord`: Discord通知に関する設定
  - `token`: Botトークン (String)
  - `channel`: グローバル チャンネルID (String)
  - `webhook_url`: グローバル WebHook URL (String)
  - `early`: 緊急地震速報に関する設定
    - `enable`: 有効化するか (Boolean)
    - `channel`: チャンネルID (String)
    - `webhook_url`: WebHook URL (String)
  - `jma`: 気象庁による地震情報に関する設定
    - `enable`: 有効化するか (Boolean)
    - `channel`: チャンネルID (String)
    - `webhook_url`: WebHook URL (String)
  - `nhk`: NHKによる地震情報に関する設定
    - `enable`: 有効化するか (Boolean)
    - `channel`: チャンネルID (String)
    - `webhook_url`: WebHook URL (String)
- `twitter`: Twitter通知に関する設定
  - `consumer_key`: グローバル コンシュマーキー (String)
  - `consumer_secret`: グローバル コンシュマーシークレット (String)
  - `access_token`: グローバル アクセストークン (String)
  - `access_token_secret`: グローバル アクセストークンシークレット (String)
  - `early`: 緊急地震速報に関する設定
    - `consumer_key`: コンシュマーキー (String)
    - `consumer_secret`: コンシュマーシークレット (String)
    - `access_token`: アクセストークン (String)
    - `access_token_secret`: アクセストークンシークレット (String)
  - `jma`: 気象庁による地震情報に関する設定
    - `consumer_key`: コンシュマーキー (String)
    - `consumer_secret`: コンシュマーシークレット (String)
    - `access_token`: アクセストークン (String)
    - `access_token_secret`: アクセストークンシークレット (String)
  - `nhk`: NHKによる地震情報に関する設定
    - `consumer_key`: コンシュマーキー (String)
    - `consumer_secret`: コンシュマーシークレット (String)
    - `access_token`: アクセストークン (String)
    - `access_token_secret`: アクセストークンシークレット (String)

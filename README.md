# Telegram wK_bot

a chatBot assist with **chatGPT API**, **Hugging Face** and **Telegram API**

# Table Of Content
1. [BOT FEATURES](#features)  
2. [TODO LIST](#todo)  
3. [HOW TO USE](#usage)  
4. [HOW TO CONTRIBUTE](#todo)  

## FEATURES
1. **ChatBot** (with **voice mode**)
2. **Extract Text** From Voice
3. **Generate Image** (with prompt)
4. **Youtube Downloader**
5. **Pinterest Downloader**
6. Instagram Downloader (beta)

## TODO
1. **Add:** Edit Image with Prompt 

## USAGE

1. Fork project into your Github Account

2. Add your site cookies (youtube, instagram)

3. Install requirements : 
```bash
pip install -r requirements.txt
```

4. Go to [render.com](https://render.com)

5. Register, Login and **Create python3 project**

6. Connect **`render.com`** app to **`Github`** repository

7. Create `HuggingFace API`, `OPEN_AI API` and add them into **render Dasboard**

8. Create a bot in `@botFather` in telegram

9. Set telegram webhook (like this) :
```bash
curl -X POST https://api.telegram.org/bot{YOUR_BOT_TOKEN}/setWebhook?url={YOUR_RENDER_APP_LINK}
```
10. Customize Bot Menu and Enjoy.

## CONTRIBUTE
1. **Fork** The Project
2. Make the Changes (**Your own idea** and **features** or from **[todo](#todo) List** )
3. **Push**
